const sessionManager=require("./session_manager");
const mapManger=require("./mapManager");
const { Bullet } = require("./Player");

class Room {
    constructor(host, roomType) {
        this.roomType=roomType;
        this.mapProp=mapManger.getMapProp(roomType);
        this.mapData=this.mapProp.map;
        this.tree=this.mapProp.tree;
        this.availableArea=this.mapProp.availableArea;

        this.host = host;
        this.activePlayers = new Set();
        this.connectedPlayers=new Set();
        this.bullets=[];
        this.isRunning = false;
        this.lastUpdateTime = null;
        this.interval=16;
        this.speed=this.mapData.speed;  

        this.xOpf = 32; // Assuming constants; adjust if needed
        this.yOpf = 32;

        this.gameWidth=this.mapData.width*this.mapData.tileWidth;
        this.gameHeight=this.mapData.height*this.mapData.tileHeight;

        this.ranks=[];

        this.initializePlayer(host);
    }

    initializePlayer(player) {
        // Assign the player to this room
        player.linkRoom(this);
        const playerSizeInTiles=1;
        let availableArea=this.mapProp.availableArea;
    
        // Select a random valid range
        const validRanges = availableArea.filter(range => (range.end - range.start + 1) >= playerSizeInTiles);
        if (validRanges.length === 0) {
            throw new Error("No valid positions available for the player.");
        }
    
        // Pick a random range and position the player
        const selectedRange = validRanges[Math.floor(Math.random() * validRanges.length)];
        const startTile = Math.floor(Math.random() * ((selectedRange.end - playerSizeInTiles) - selectedRange.start + 1)) + selectedRange.start;
        const endTile = startTile + playerSizeInTiles;
    
        player.xPos = Math.round((startTile % this.mapData.width) * this.mapData.tileWidth - player.xOffset); // Calculate x position
        player.yPos = Math.round(Math.floor(startTile / this.mapData.height) * this.mapData.tileHeight - player.yOffset); // Calculate y position
    
        // Update availableArea by removing the occupied tiles
        const updatedRanges = [];
        availableArea.forEach(range => {
            if (range.end < startTile || range.start > endTile) {
                // No overlap
                updatedRanges.push(range);
            } else {
                // Partial overlaps: split the range if necessary
                if (range.start < startTile) {
                    updatedRanges.push({ start: range.start, end: startTile - 1 });
                }
                if (range.end > endTile) {
                    updatedRanges.push({ start: endTile + 1, end: range.end });
                }
            }
        });
    
        // Update the availableArea array
        this.mapProp.availableArea = updatedRanges;
    
        // Ensure player starts within bounds (optional, depends on your range logic)
        if (player.xPos < 0) player.xPos = 0;
        if (player.yPos < 0) player.yPos = 0;
        if (player.xPos > player.XCons) player.xPos = player.XCons;
        if (player.yPos > player.YCons) player.yPos = player.YCons;

        this.activePlayers.add(player);
        this.connectedPlayers.add(player);
    }

    addPlayer(player) {
        this.activePlayers.forEach(existingPlayer => {
            existingPlayer.ws.send(JSON.stringify({
                type: "new-member",
                des: player.playername
            }));
        });

        const playersObj = Array.from(this.activePlayers).map(p => ({
            uid: p.uid,
            playername: p.playername
        }));
        
        this.initializePlayer(player);

        return player.ws.send(JSON.stringify({
            req: "joinroom",
            success: true,
            roomType: this.roomType,
            des: playersObj
        }));
    }

    gameLoop() {
        if (!this.isRunning) return;
    
        const currentTime = Date.now();
        const elapsed = currentTime - (this.lastUpdateTime || currentTime);
        this.lastUpdateTime = currentTime;
    
        // // Update each player's position based on `elapsed` time
        // this.activePlayers.forEach(player => {
        //     player.xPos += Math.floor((Math.random() * 3 - 1) * (elapsed / this.interval));
        //     player.yPos += Math.floor((Math.random() * 3 - 1) * (elapsed / this.interval));
        // });
    
        // Collect the positions of all players
        const positions = {};  // Using an object to store player positions by uid

        positions.bullets=[];
        this.bullets = this.bullets.filter(bullet => {

            const prevX=bullet.xPos;
            const prevY=bullet.yPos;
        
            switch (bullet.direction) {
                case 0: 
                    bullet.yPos -= bullet.speed;
                    if(bullet.yPos-bullet.xOffset<=0) {
                        positions.bullets.push({ xPos: bullet.xPos, yPos: bullet.xOffset, direction: bullet.direction });
                        return false;
                    }
                    break;
                case 1:
                    bullet.xPos += bullet.speed;
                    if(bullet.xPos+bullet.xOffset>=this.gameWidth) {
                        positions.bullets.push({ xPos: this.gameWidth-bullet.xOffset, yPos: bullet.yPos, direction: bullet.direction });
                        return false;
                    }
                    break;
                case 2:
                    bullet.yPos += bullet.speed;
                    if(bullet.yPos+bullet.xOffset>=this.gameHeight) {
                        positions.bullets.push({ xPos: bullet.xPos, yPos: this.gameHeight-bullet.xOffset, direction: bullet.direction });
                        return false;
                    }
                    break;
                case 3:
                    bullet.xPos -= bullet.speed;
                    if(bullet.xPos-bullet.xOffset<=0) {
                        positions.bullets.push({ xPos: bullet.xOffset, yPos: bullet.xOffset, direction: bullet.direction });
                        return false;
                    }
                    break;
            }
        
            // Correct position if the bullet exceeds its range
            if (bullet.getDistance() >= bullet.range) {
                if (bullet.direction === 0) { // Up
                    bullet.yPos = bullet.origY - bullet.range;
                } else if (bullet.direction === 1) { // Right
                    bullet.xPos = bullet.origX + bullet.range;
                } else if (bullet.direction === 2) { // Down
                    bullet.yPos = bullet.origY + bullet.range;
                } else if (bullet.direction === 3) { // Left
                    bullet.xPos = bullet.origX - bullet.range;
                }

                positions.bullets.push({ xPos: bullet.xPos, yPos: bullet.yPos, direction: bullet.direction });
                return false;
            }

            const xOff=(bullet.direction==0 || bullet.direction==2)?bullet.yOffset:bullet.xOffset;
            const yOff=(bullet.direction==0 || bullet.direction==2)?bullet.xOffset:bullet.yOffset;

            const minX=bullet.xPos-xOff;
            const minY=bullet.yPos-yOff;
            const maxX=minX+xOff*2;
            const maxY=minY+yOff*2;

            const query = { minX, minY, maxX, maxY };
            const collisions = this.tree.search(query);
            
            if(collisions.length>0) {
                positions.bullets.push({ xPos: bullet.xPos, yPos: bullet.yPos, direction: bullet.direction, exploded: true }); //Direction 6 refers to explosion
                return false;
            }

            for(let player of this.activePlayers) {
                // if (player === bullet.owner) return; // Skip if the player is the bullet owner (no friendly fire)
    
                const playerMinX = player.xPos - player.xOffset;
                const playerMinY = player.yPos - player.yOffset;
                const playerMaxX = playerMinX + player.width;
                const playerMaxY = playerMinY + player.height;
    
                // Check for overlap between bullet and player
                if (
                    minX < playerMaxX &&
                    maxX > playerMinX &&
                    minY < playerMaxY &&
                    maxY > playerMinY
                ) {
                    // Bullet hits the player
                    const bulletPos={ xPos: bullet.xPos, yPos: bullet.yPos, direction: bullet.direction, collosion: "hit" };
                    positions.bullets.push(bulletPos); // Direction 6 refers to explosion
                    
                    player.health-=bullet.damage;
                    if(player.health <= 0) {
                        bulletPos.collosion="exploded";
                        player.ws.send(JSON.stringify({
                            type: "death",
                            des: bullet.player
                        }));
                        this.activePlayers.delete(player);
                        this.ranks.unshift(player.playername);

                        if(this.activePlayers.size==1) {
                            this.stopGame();
                            const remainingPlayer=this.activePlayers.values().next().value;
                            this.ranks.unshift(remainingPlayer.playername);
                            this.connectedPlayers.forEach(player => {
                                player.ws.send(JSON.stringify({
                                    "type": "finish",
                                    des: this.ranks
                                }));
                                // player.ws.close();
                            });
                            sessionManager.deleteRoom(this.host.uid);
                            return
                        }
                    }
    
                    return false; // Remove the bullet after it hits the player
                }
            };
        
            positions.bullets.push({ xPos: bullet.xPos, yPos: bullet.yPos, direction: bullet.direction });

            return true; // Keep the bullet
        });

        positions.players={};
        this.activePlayers.forEach(player => {
            positions.players[player.uid] = { playername: player.playername, xPos: player.xPos, yPos: player.yPos, direction: player.direction, health: player.health };
        });
    
        // Broadcast the positions to each player
        this.connectedPlayers.forEach(player => {
            player.ws.send(JSON.stringify({
                type: "update-position",
                positions: positions
            }));
        });
    
        // Schedule the next update based on `this.interval`
        const nextDelay = Math.max(0, this.interval - (Date.now() - currentTime));
        setTimeout(() => this.gameLoop(), nextDelay);
    }
    

    startGame() {
        this.isRunning = true;
        this.lastUpdateTime = Date.now();

        const positions = {};  // Using an object to store player positions by uid
        this.activePlayers.forEach(player => {
            positions[player.uid] = { xPos: player.xPos, yPos: player.yPos, direction: player.direction };
        });

        this.activePlayers.forEach(player => {
            player.ws.send(JSON.stringify({
                type: "start-game",
                success: true,
                players: positions
            }));
        });
        this.gameLoop(); // Start the game loop
    }

    stopGame() {
        this.isRunning = false;
    }

    getPlayers() {
        return this.activePlayers;
    }

    updatePlayerPosition(player, direction) {

        if(direction==5) {
            //Fire bullet event
            const bullet=new Bullet(player)
            this.bullets.push(bullet);
            return;
        }

        if (!this.activePlayers.has(player)) {
            return false;
        }
    
        player.direction = direction;
        let newX = player.xPos;
        let newY = player.yPos;
    
        // Update player's position based on direction
        switch (direction) {
            case 0: // Up
                newY -= this.speed;
                break;
            case 2: // Down
                newY += this.speed;
                break;
            case 3: // Left
                newX -= this.speed;
                break;
            case 1: // Right
                newX += this.speed;
                break;
        }
    
        const minX=newX-player.xOffset;
        const minY=newY-player.yOffset;
        const maxX=minX+player.width;
        const maxY=minY+player.height;

        const query = { minX, minY, maxX, maxY };
        const collisions = this.tree.search(query);
    
        // Resolve collisions
        for (const object of collisions) {
            // Adjust position to 1 pixel away from the collision boundary
            if (direction === 0) { // Moving up
                newY = object.maxY + 1 + player.yOffset;
            } else if (direction === 2) { // Moving down
                newY = object.minY - 1 - player.yOffset;
            } else if (direction === 3) { // Moving left
                newX = object.maxX + 1 + player.xOffset;
            } else if (direction === 1) { // Moving right
                newX = object.minX - 1 - player.xOffset;
            }
        }
    
        // Check for collisions with other players
        for (const otherPlayer of this.activePlayers) {
            if (otherPlayer === player) continue; // Skip self
    
            const otherMinX = otherPlayer.xPos - otherPlayer.xOffset;
            const otherMinY = otherPlayer.yPos - otherPlayer.yOffset;
            const otherMaxX = otherMinX + otherPlayer.width;
            const otherMaxY = otherMinY + otherPlayer.height;
    
            // Check for overlap between player and other player
            if (
                minX < otherMaxX &&
                maxX > otherMinX &&
                minY < otherMaxY &&
                maxY > otherMinY
            ) {
                // Collision detected with another player, adjust the position
                // Example logic: stop movement if collision is detected
                if (direction === 0) { // Moving up
                    newY = otherMaxY + 1 + player.yOffset; // Move just below the other player
                } else if (direction === 2) { // Moving down
                    newY = otherMinY - 1 - player.yOffset; // Move just above the other player
                } else if (direction === 3) { // Moving left
                    newX = otherMaxX + 1 + player.xOffset; // Move just right of the other player
                } else if (direction === 1) { // Moving right
                    newX = otherMinX - 1 - player.xOffset; // Move just left of the other player
                }
                break; // Stop checking further once a collision is detected
            }
        }
    
        // Apply boundary constraints
        player.xPos = Math.max(player.xOffset, Math.min(newX, player.XCons));
        player.yPos = Math.max(player.yOffset, Math.min(newY, player.YCons));
    }
}

module.exports = { Room };