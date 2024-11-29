const http=require("http");
const express=require("express");
const WebSocket = require("ws");
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const jwt = require("jsonwebtoken");
const path=require('path')
const multer=require('multer');
const fsSync=require('fs');
const fs=require("fs/promises");
const AdmZip = require('adm-zip');

const { Player }=require("./Player");
const { Room }=require("./Room");
const { initialize }=require("./mapManager")

const gamedata=require("./game_data.json");

const app=express();
const server=http.createServer(app);
const wss = new WebSocket.Server({ noServer: true });

const secretKey = crypto.randomBytes(32).toString('hex');

const mapsDir=path.join(__dirname, 'content/maps');
const archivedDir=path.join(mapsDir, "archived");
const extractedDir=path.join(mapsDir, "extracted");
const metadataFile = path.join(mapsDir, 'tilemaps.json');

if(!fsSync.existsSync(archivedDir)) {
    fsSync.mkdirSync(archivedDir, { recursive: true});
}
if(!fsSync.existsSync(extractedDir)) {
    fsSync.mkdirSync(extractedDir);
}
if (!fsSync.existsSync(metadataFile)) 
    fsSync.writeFileSync(metadataFile, JSON.stringify([]));

const storage=multer.diskStorage({
    destination: (req, file, cb)=>{
        cb(null, archivedDir);
    },
    filename: (req, file, cb) => {
        // Ensure the file name is unique
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + path.extname(file.originalname));
    }
});

const upload=multer({storage: storage});

const sessionManager=require("./session_manager")
server.on('upgrade', (request, socket, head)=>{
    const path=request.url;

    if(path==="/ws") {
        wss.handleUpgrade(request, socket, head, ws=>{
            wss.emit('connection', ws, request);
        });
    } else {
        socket.destroy();
    }
})

wss.on('connection', ws => {
    console.log("New client connected");

    onMessage(ws, (ws, message, uid, playerData) => {
        let roomId, room;
        switch (message.type) {
            case "updatePos":
                sessionManager.getUserSession(uid).updatePos(message.direction);
                // console.log("Position update: "+message.xPos+", "+message.yPos)
                break;
            case "newroom":
                let roomType=message.roomType || 0;
                if(roomType >= metadataFile.length) {
                    roomType=0;
                }
                sessionManager.addRoom(new Room(sessionManager.getUserSession(uid), roomType)); 
                return ws.send(JSON.stringify({
                    req: "newroom",
                    success: true,
                    roomType: roomType,
                    des: uid
                }));
                break;

            case "joinroom":
                roomId = message.roomId;
                room=sessionManager.getRoom(roomId);
                if (!roomId || !room) {
                    return ws.send(JSON.stringify({
                        req: "joinroom",
                        success: false,
                        des: "room-not-found"
                    }));
                }

                room.addPlayer(sessionManager.getUserSession(uid));

                break;

            case "start-game":
                room=sessionManager.getRoom(uid);
                if(!room) {
                    return ws.send(JSON.stringify({
                        req: "start-game",
                        success: false,
                        des: "no-room"
                    }));
                }

                room.startGame();
                break;
        }
    })
});

function onMessage(ws, handler) {
    ws.on("message", data => {
        let message;
        try {
            message = JSON.parse(data);
        } catch(err) {
            console.error(err)
            return ws.send(JSON.stringify({
                success: "false",
                des: "internal-error"
            }));
        }
        if (message.type == "connect") {
            console.log("New connect")
            const playername = message.playername;
            if (!playername) {
                return ws.send(JSON.stringify({req:"connect", success: false, des: "invalid-request" }));
            }

            const uid = uuidv4();
            const token = jwt.sign({ uid, playername }, secretKey, { expiresIn: '1h' });
            const player = new Player(uid, playername, ws);
            sessionManager.addUserSession(uid, player) // Store player instance directly

            return ws.send(JSON.stringify({
                req: "connect",
                success: true,
                token: token,
                uid: uid
            }));
        }

        if (!message.token) {
            return ws.send(JSON.stringify({
                success: false,
                des: "no-token"
            }));
        }

        const playerData = verifyUser(message.token);
        const uid = playerData.uid;
        if (!uid) {
            return ws.send(JSON.stringify({
                success: false,
                des: "not-authorised"
            }));
        }

        handler(ws, message, uid, playerData);
    });
}

function verifyUser(token) {
    try {
        const decoded = jwt.verify(token, secretKey);
        return decoded;
    } catch (error) {
        return false;
    }
}

// const PORT=8000;
// server.listen(PORT, ()=>{
//     console.log("Server is listening on "+PORT);
// });

app.use('/static', express.static(path.join(__dirname, 'content')));

app.post('/upload', upload.fields([
    { name: 'tilemapFile', maxCount: 1 },
    { name: 'thumbnailFile', maxCount: 1 }
]), async (req, res) => {
    const { mapName, description } = req.body;
    const speed = req.body.speed || 10;

    // Validate required fields
    if (!req.files || !req.files.tilemapFile || !req.files.tilemapFile[0] || !mapName || !description) {
        return res.status(400).send('Map name, description, and tilemap file are required.');
    }

    const tilemapFile = req.files.tilemapFile[0];
    const thumbnailFile = req.files.thumbnailFile ? req.files.thumbnailFile[0] : null;

    const uploadedTilemapPath = tilemapFile.path;
    const archiveFolder = path.join(extractedDir, path.parse(tilemapFile.filename).name);

    const baseDir = path.join(__dirname, "content");

    // Prepare metadata for the new tilemap
    const newTilemap = {
        name: mapName,
        description,
        archivePath: path.relative(baseDir, uploadedTilemapPath),
        extractedPath: path.relative(baseDir, archiveFolder),
        speed: speed,
        uploadedAt: new Date().toISOString(),
        thumbnailPath: thumbnailFile ? path.relative(baseDir, thumbnailFile.path) : null,
    };

    try {
        // Create the folder structure
        await fs.mkdir(archiveFolder, { recursive: true });

        // Extract only the .tmx files
        const zip = new AdmZip(uploadedTilemapPath);
        const zipEntries = zip.getEntries(); // Get all entries in the archive

        zipEntries.forEach(entry => {
            zip.extractEntryTo(entry, archiveFolder, true);
        });

        // Update metadata
        const metadataContent = await fs.readFile(metadataFile, 'utf-8').catch(() => '[]');
        const metadata = JSON.parse(metadataContent);
        metadata.push(newTilemap);
        await fs.writeFile(metadataFile, JSON.stringify(metadata, null, 2));

        res.status(200).send({
            message: 'Tilemap and thumbnail uploaded, extracted .tmx files, and metadata saved successfully!',
            tilemap: newTilemap,
        });
    } catch (error) {
        console.error(error);
        res.status(500).send('Server error while processing the files.');
    }
});

app.get('/tilemaps', async (req, res) => {
    try {
        const metadataContent = await fs.readFile(metadataFile, 'utf-8');
        const metadata = JSON.parse(metadataContent || '[]');
        res.status(200).send(metadata);
    } catch (error) {
        console.error(error);
        res.status(500).send('Server error while fetching metadata.');
    }
});


async function startServer() {
    await initialize();

    const PORT=8000;
    server.listen(PORT, ()=>{
        console.log("Server is listening on "+PORT);
    });
}

startServer().then(()=>{
    console.log("Server started successfully");
})