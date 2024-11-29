const userSessions = {}; // Keeps the sessions
const rooms={};

function addUserSession(uid, player) {
    userSessions[uid] = player;
}

function removeUserSession(uid) {
    delete userSessions[uid];
}

function getUserSession(uid) {
    return userSessions[uid];
}

function getAllUserSessions() {
    return userSessions;
}

function addRoom(room) {
    rooms[room.host.uid]=room;                                                                                                                                                                                                                                    
}

function deleteRoom(uid) {
    delete rooms[uid];
}

function getRoom(uid) {
    return rooms[uid];
}

module.exports = {
    addUserSession,
    removeUserSession,
    getUserSession,
    getAllUserSessions,
    addRoom,
    getRoom,
    deleteRoom
};