let ws;
let peerConnection;
let dataChannel;
let isInitiator = false;
let localStream = null;

const baseUrl = "https://api.openai.com/v1/realtime";
const model = "gpt-live-transcribe";
    

const connectButton = document.getElementById("connect");

const audioEl = document.getElementById("audio");

async function startRealtimeChat() {
    // 1. Get the secure ephemeral token from your server route
    // const sessionResponse = await fetch("/session");
    // const sessionData = await sessionResponse.json();
    // const EPHEMERAL_KEY = sessionData.client_secret;

    const { value: EPHEMERAL_KEY } = await fetch("/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ targetLanguage: "en" }),
    }).then((response) => response.json());

    // 2. Initialize the RTCPeerConnection 
    const pc = new RTCPeerConnection();

    // 3. Play incoming remote audio streams from the model
    audioEl.autoplay = true;
    
    pc.ontrack = (event) => {
        // Assign the remote audio track to our DOM element
        audioEl.srcObject = event.streams[0];
    };

    // 4. Request and add local microphone track
    const localStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    pc.addTrack(localStream.getTracks()[0]);

    // 5. Establish a Data Channel for tool usage or handling text events (Optional)
    const dataChannel = pc.createDataChannel("oai-events");
    dataChannel.onmessage = (event) => {
        const serverEvent = JSON.parse(event.data);
        console.log("Received event from OpenAI:", serverEvent);
    };

    // 6. Generate the SDP offer detailing capabilities
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // 7. Post the local SDP offer to OpenAI's real-time WebRTC route
    const sdpResponse = await fetch(`${baseUrl}/calls?model=${model}`, {
        method: "POST",
        body: offer.sdp,
        headers: {
            "Authorization": `Bearer ${EPHEMERAL_KEY}`,
            "Content-Type": "application/sdp"
        },
    });

    // 8. Accept the SDP response answer back from OpenAI
    const answerSdp = await sdpResponse.text();
    const answer = {
        type: "answer",
        sdp: answerSdp,
    };
    
    await pc.setRemoteDescription(answer);
    console.log("WebRTC connection established successfully!");
}

connectButton.onclick = () => {
    startRealtimeChat();
};
