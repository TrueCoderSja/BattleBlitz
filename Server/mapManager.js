const tmxParser = require("tmx-parser");
const fs = require("fs");
const path = require("path");

let RBush; // Placeholder for RBush
const mapProps=[];

class MapProp {
    constructor(map, tree, availableArea) {
        this.map=map;
        this.tree=tree;
        this.availableArea=availableArea;
    }
}

async function loadRBush() {
    RBush = (await import("rbush")).default;
}

function parseTMXFile(filePath) {
    return new Promise((resolve, reject) => {
        tmxParser.parseFile(filePath, (err, map) => {
            if (err) {
                return reject(err);
            }
            resolve(map);
        });
    });
}

async function loadTMX(filePath, speed) {
    try {
        const map = await parseTMXFile(filePath);
        map.speed = speed;

        const tree = new RBush();
        const availableRanges=[];

        const objLayers = map.layers.filter((layer) => layer.type === "object");
        objLayers.forEach((objLayer) => {
            objLayer.objects.forEach((obj) => {
                const width = obj.width || 0;
                const height = obj.height || 0;
                const minX = obj.x;
                const minY = obj.y;
                const maxX = obj.x + width;
                const maxY = obj.y + height;

                tree.insert({ minX, minY, maxX, maxY, type: obj.type || "collision" });
            });
        });

        const mapWidth = map.width;
        const mapHeight = map.height;
        const tileWidth = map.tileWidth;
        const tileHeight = map.tileHeight;

        // Check if a tile is free
        const checkFreeTile = (tileIndex) => {
            const row = Math.floor(tileIndex / mapWidth);
            const col = tileIndex % mapWidth;
            const x1 = col * tileWidth;
            const y1 = row * tileHeight;
            const x2 = x1 + tileWidth;
            const y2 = y1 + tileHeight;

            const results = tree.search({ minX: x1, minY: y1, maxX: x2, maxY: y2 });
            return results.length === 0;
        };

        // Determine free ranges
        let start = null;

        for (let tileIndex = 0; tileIndex < mapWidth * mapHeight; tileIndex++) {
            if (checkFreeTile(tileIndex)) {
                if (start === null) {
                    start = tileIndex; // Start of a new free range
                }
            } else {
                if (start !== null) {
                    availableRanges.push({ start: start, end: tileIndex }); // End of the current free range
                    start = null;
                }
            }
        }

        // Add the last range if it didn't end
        if (start !== null) {
            availableRanges.push({ start: start + 1, end: mapWidth * mapHeight });
        }

        const mapProp = new MapProp(map, tree, availableRanges);
        mapProps.push(mapProp);
    } catch (err) {
        console.error(`Failed to load TMX file ${filePath}:`, err);
    }
}


async function loadMaps() {    
    const baseDir=path.join(__dirname, "content");
    const tilemaps = require("./content/maps/tilemaps.json");
    for (const tilemap of tilemaps) {
        try {
            const extractedPath=path.join(baseDir, tilemap.extractedPath);
            const files = fs.readdirSync(extractedPath);
            const tmxFiles = files.filter((file) => path.extname(file) === ".tmx");
            for (const file of tmxFiles) {
                await loadTMX(path.join(extractedPath, file), tilemap.speed);
            }
        } catch (err) {
            console.error(`Error loading maps from ${extractedPath}:`, err);
        }
    }
}

async function initialize() {
    try{
        await loadRBush();
        await loadMaps();
    } catch(err) {
        console.error(err);
    }
}

function getMapProp(index)  {
    return mapProps[index];
}

module.exports = {
    initialize,
    getMapProp
};
