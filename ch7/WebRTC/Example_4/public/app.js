const status = document.getElementById("status");
const messages = document.getElementById("messages");

const connectButton = document.getElementById("connect");
const createOfferButton = document.getElementById("create_offer");
const sendButton = document.getElementById("send");
const disconnectButton = document.getElementById("disconnect");
const messageTextarea = document.getElementById("message");

let ws;
let peerConnection;
let dataChannel;
let isInitiator = false;

// STUN server
const configuration = {
    iceServers: [{urls: "stun:stun.l.google.com:19302"}]
};

// --------------------------------------------------
// WebSocket signaling
// --------------------------------------------------
function connectSignaling() {
    ws = new WebSocket(
        `ws://${location.host}`
    );
    ws.onopen = () => {
        log("Connected to signaling server");
        status.textContent = "Connected to signaling server";
    };

    ws.onmessage = async (event) => {
        const message = JSON.parse(event.data);
        await handleSignal(message);
    };

    ws.onclose = () => {
        log("Signaling disconnected");
    };
}

// --------------------------------------------------
// Create PeerConnection
// --------------------------------------------------
function createPeerConnection() {
    peerConnection = new RTCPeerConnection(configuration);
        
    // ICE candidate
    peerConnection.onicecandidate =
        event => {
            if (event.candidate) {
                sendSignal({
                    type: "candidate",
                    candidate: event.candidate
                });
            }
        };

    // Connection state
    peerConnection.onconnectionstatechange =
        () => {
            log(
                "Connection state: " +
                peerConnection.connectionState
            );
        };

    // Remote DataChannel
    peerConnection.ondatachannel =
        event => {
            log("Remote DataChannel received");
            // P2P DataChannel OPEN for Remote
            setupDataChannel(event.channel);
        };
}

// --------------------------------------------------
// DataChannel
// --------------------------------------------------
function setupDataChannel(channel) {
    dataChannel = channel;
    dataChannel.onopen = () => {
        log("P2P DataChannel OPEN");
        status.textContent = "P2P Connected";
    };

    dataChannel.onclose = () => {
        log("DataChannel closed");
    };

    dataChannel.onmessage = event => {
        log("Remote: " + event.data);
    };
}

// --------------------------------------------------
// Create offer
// --------------------------------------------------
async function createOffer() {
    createPeerConnection();

    dataChannel = peerConnection.createDataChannel("chat");
    // P2P DataChannel OPEN for Local
    setupDataChannel(dataChannel); 

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    sendSignal({
        type: "offer",
        offer: offer
    });
}

// --------------------------------------------------
// Close Connection
// --------------------------------------------------
function closeConnection() {
    ws.close(1000, 'User logged out');
    peerConnection.close();
    peerConnection = null;
}

// --------------------------------------------------
// Handle signaling
// --------------------------------------------------
async function handleSignal(message) {
    if (message.type === "offer") {
        log("Received offer");
        createPeerConnection();
        
        await peerConnection.setRemoteDescription(
            message.offer
        );

        const answer =
            await peerConnection.createAnswer();

        await peerConnection.setLocalDescription(
            answer
        );

        sendSignal({
            type: "answer",
            answer: answer
        });
    }
    else if (message.type === "answer") {
        log("Received answer");
        await peerConnection.setRemoteDescription(
            message.answer
        );
    }
    else if (message.type === "candidate") {
        try {
            await peerConnection.addIceCandidate(
                message.candidate
            );
        } catch (error) {
            console.error(
                "ICE error:",
                error
            );
        }
    }
    else if (message.type === "disconnect") {
        log("Disconnect");
        await peerConnection.setRemoteDescription(
            message.answer
        );
    }
}

// --------------------------------------------------
// Send signaling message
// --------------------------------------------------
function sendSignal(message) {
    ws.send(
        JSON.stringify(message)
    );
}

// --------------------------------------------------
// UI
// --------------------------------------------------
connectButton.onclick = () => {
    connectSignaling();
};

createOfferButton.onclick = () => {
    createOffer();
};

disconnectButton.onclick = () => {
    closeConnection();
};

sendButton.onclick = () => {
    if (
        dataChannel &&
        dataChannel.readyState === "open"
    ) {
        dataChannel.send(messageTextarea.value);
        log(
            "Me: " + messageTextarea.value
        );
    } else {
        log(
            "DataChannel is not connected"
        );
    }
};

// --------------------------------------------------
// Logging
// --------------------------------------------------
function log(message) {
    const div = document.createElement("div");
    div.textContent = new Date().toLocaleTimeString()
        + " - " + message;
    messages.appendChild(div);
}