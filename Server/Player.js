const gamedata=require("./game_data.json");
// const sessionManager=require("./session_manager")

class Player {
    constructor(uid, playername, ws) {
        this.uid = uid;
        this.playername = playername;
        this.health=5;
        this.ws = ws;

        this.width=32;
        this.height=32;
        this.xOffset=Math.round(this.width/2);
        this.yOffset=Math.round(this.height/2);

        this.direction=Math.floor(Math.random()*4);

        console.log("Player Initialized");
    }

    linkRoom(room) {
        this.room=room;
        this.XCons=room.gameWidth-this.xOffset;
        this.YCons=room.gameHeight-this.yOffset;
    }

    updatePos(direction) {
        this.room.updatePlayerPosition(this, direction);
    }

    // updatePos(direction) {
    //     const speed=gamedata.speed;
    //     console.log("Move in direction: "+direction);
    //     this.direction=direction;
    //     switch(direction) {
    //         case 0:
    //             this.yPos-=speed
    //             break;
    //         case 2:
    //             this.yPos+=speed
    //             break;
    //         case 3:
    //             this.xPos-=speed
    //             break;
    //         case 1:
    //             this.xPos+=speed
    //             break;
    //     }
    //     if(this.xPos<0)
    //         this.xPos=0;
    //     else if(this.xPos>this.XCons)
    //         this.xPos=this.XCons;
        
    //     if(this.yPos<0)
    //         this.yPos=0;
    //     else if(this.yPos>this.YCons)
    //         this.yPos=this.YCons;
    // }
}


class Bullet {
    constructor(player) {
        this.speed=20;
        this.damage=1;
        this.range=540;

        this.width=32;
        this.height=10;

        this.xOffset=Math.round(this.width/2);
        this.yOffset=Math.round(this.height/2);

        this.direction=player.direction;
        this.xPos=player.xPos;
        this.yPos=player.yPos;

        switch(this.direction) {
            case 0:
                this.yPos-=player.height-this.speed;
                break;
            case 2:
                this.yPos+=player.height-this.speed;
                break;
            case 1:
                this.xPos+=player.height-this.speed;
                break;
            case 3:
                this.xPos-=player.height-this.speed;
                break;
        }
        
        this.origX=this.xPos;
        this.origY=this.yPos;
    }

    getDistance() {
        return Math.abs(this.origX - this.xPos) || Math.abs(this.origY - this.yPos);
    }
}

module.exports={ Player, Bullet };