const realtime_url = "https://api.openai.com/v1/realtime/translations/calls"
const subtitles = document.getElementById("subtitles");
const targetLanguage = document.getElementById("targetLanguage");
const startButton = document.querySelector("#startButton");
const stopButton = document.querySelector("#stopButton");
let sourceStream;

async function startRealtimeChat() {
    // get Client Secret
    const { value: clientSecret } = await fetch("/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ "Language": targetLanguage.value }),
    }).then((response) => response.json());

    // capture audio from microphone
    sourceStream = await navigator.mediaDevices.getUserMedia({
      audio: true,
    });

    // create RTCPeerConnection
    const pc = new RTCPeerConnection();
    pc.addTrack(sourceStream.getAudioTracks()[0], sourceStream);

    // create Audio object
    const translatedAudio = new Audio();
    translatedAudio.autoplay = true;
    pc.ontrack = ({ streams }) => {
      translatedAudio.srcObject = streams[0];
    };

    // create Data Channel
    const events = pc.createDataChannel("oai-events");
    events.onmessage = ({ data }) => {
      const event = JSON.parse(data);
      if (event.type === "session.output_transcript.delta") {
        subtitles.textContent += event.delta;
      }
      // console.log(subtitles.textContent.trim())
      if (subtitles.textContent.trim().endsWith('.')) {
        subtitles.textContent += "\n";
      }
    };

    // create Offer
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    // get translated audio from remote
    const sdpResponse = await fetch(realtime_url,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${clientSecret}`,
          "Content-Type": "application/sdp",
        },
        body: offer.sdp,
      }
    );

    if (!sdpResponse.ok) {
      throw new Error(await sdpResponse.text());
    }

    await pc.setRemoteDescription({
      type: "answer",
      sdp: await sdpResponse.text(),
    });
};

function stopRealtimeChat() {
    sourceStream.getTracks().forEach(function(track) {
      track.stop();
    });
};

startButton.onclick = () => {
    startRealtimeChat();
    startButton.disabled = true;
    stopButton.disabled = false;
};

stopButton.onclick = () => {
    stopRealtimeChat();
    stopButton.disabled = true;
    startButton.disabled = false;
};
