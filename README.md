<h1>Wajeeha Transcribe</h1>

<p>A lightweight Windows GUI for offline speech-to-text transcription using Cactus Whistle (Needle).</p>
<img width="616" height="607" alt="image" src="https://github.com/user-attachments/assets/81e3df61-f1db-4d82-a7a6-a2268ff5c237" />

<p>Wajeeha Transcribe is a simple desktop application that converts speech from WAV audio files or microphone recordings into text. It provides an easy-to-use graphical interface, automatically splits longer recordings into smaller chunks, and saves the resulting transcript to a <code>.txt</code> file.</p>

<h2>Features</h2>
<ul>
  <li><strong>WAV File Transcription:</strong> Browse and select an existing <code>.wav</code> audio file.</li>
  <li><strong>Microphone Recording:</strong> Record audio directly from your microphone.</li>
  <li><strong>Automatic Audio Splitting:</strong> Automatically divides audio longer than 28 seconds into smaller chunks to stay within the model's 30-second limit.</li>
  <li><strong>Smart Chunk Boundaries:</strong> Attempts to split audio at quieter points to minimize interruptions between words.</li>
  <li><strong>Text Export:</strong> Save the generated transcript to a <code>.txt</code> file of your choice.</li>
  <li><strong>Offline Support:</strong> Uses locally stored model weights and engine libraries after initial setup.</li>
  <li><strong>Simple GUI:</strong> Clean and intuitive Windows desktop interface.</li>
  <li><strong>Background Processing:</strong> Performs model setup and transcription in background threads to keep the interface responsive.</li>
</ul>

<h2>How It Works</h2>
<p>Wajeeha Transcribe uses <strong>Cactus Whistle (Needle)</strong> as its speech-to-text engine.</p>
<p>The application follows this workflow:</p>
<ol>
  <li>Select a WAV audio file or record audio using your microphone.</li>
  <li>Choose where to save the transcript.</li>
  <li>Click <strong>Run transcription</strong>.</li>
  <li>The application loads and processes the audio.</li>
  <li>Longer recordings are automatically divided into approximately 28-second chunks.</li>
  <li>Each chunk is transcribed using the Whistle model.</li>
  <li>Individual transcripts are combined into one continuous text.</li>
  <li>The final transcript is saved as a UTF-8 <code>.txt</code> file.</li>
</ol>

<h2>Requirements</h2>

<h3>System Requirements</h3>
<ul>
  <li>Windows 10 or Windows 11.</li>
  <li>Microphone (optional, only required for recording).</li>
  <li>Internet connection for the initial model and engine download, unless these files are bundled with the application.</li>
  <li>Sufficient disk space for the application, model, and dependencies.</li>
</ul>

<h3>Python Requirements</h3>
<p>If running from source, you need:</p>
<ul>
  <li>Python 3.10 or a compatible version supported by the project dependencies.</li>
  <li><code>pip</code> (Python package manager).</li>
</ul>
<p>The Python dependencies are listed in <code>requirements.txt</code>.</p>

<h2>Project Structure</h2>
<p>The project is organized as follows:</p>
<pre><code>Wajeeha-Transcribe/
│
├── main.py                  # Main application and GUI
├── requirements.txt         # Python dependencies
├── build.bat                # Windows build script
├── README.md                # Project documentation
│
├── models/
│   └── whistle.cact         # Whistle model weights
│
├── engine/
│   └── *.dll                # Needle engine libraries
│
├── WT.ico                   # Application icon
└── WT.png                   # Application icon (PNG fallback)
</code></pre>
<blockquote>
  <p><strong>Note:</strong> The <code>models</code> and <code>engine</code> directories may be generated or populated during the initial setup or build process.</p>
</blockquote>

<h2>Installation</h2>

<h3>Option 1: Run from Source</h3>
<ol>
  <li>Clone or download this repository.</li>
  <li>Open Command Prompt or PowerShell in the project directory.</li>
  <li>(Optional but recommended) Create a virtual environment:
    <pre><code>python -m venv venv</code></pre>
  </li>
  <li>Activate the virtual environment:
    <pre><code>venv\Scripts\activate</code></pre>
  </li>
  <li>Install the required dependencies:
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>
  <li>Run the application:
    <pre><code>python main.py</code></pre>
  </li>
</ol>
<p>On the first run, the application checks whether the Whistle model and Needle engine libraries are available locally.</p>
<ul>
  <li>If they are missing, it attempts to download them. An internet connection is required for this initial setup.</li>
  <li>Once downloaded, the model and engine files are copied into the application's directory for subsequent offline use.</li>
</ul>

<h3>Option 2: Build the Windows Executable</h3>
<p>The project includes a <code>build.bat</code> script to automate the Windows executable build process.</p>
<p>To build the application:</p>
<ol>
  <li>Make sure Python is installed and available in <code>PATH</code>.</li>
  <li>Open the project directory.</li>
  <li>Double-click <code>build.bat</code>, or execute it from Command Prompt:
    <pre><code>build.bat</code></pre>
  </li>
</ol>
<p>The build script is intended to automate the preparation of dependencies and packaging of the application into a Windows executable.</p>
<p>The application uses a PyInstaller-compatible frozen execution structure, allowing it to locate resources relative to the executable rather than relying on the current working directory.</p>
<p><strong>Build script responsibilities:</strong></p>
<ul>
  <li>Install or prepare the required Python dependencies.</li>
  <li>Prepare the Whistle model and Needle engine libraries.</li>
  <li>Package the Python application into a Windows executable.</li>
  <li>Include the required application resources, such as icons and supporting files.</li>
</ul>
<p>The exact build options and output directory depend on the configuration in <code>build.bat</code>.</p>

<h2>Model and Engine Setup</h2>
<p>Wajeeha Transcribe requires two important components:</p>
<table>
  <thead>
    <tr><th>Component</th><th>Location</th><th>Purpose</th></tr>
  </thead>
  <tbody>
    <tr><td>Whistle Model</td><td><code>models/whistle.cact</code></td><td>Contains the speech recognition model weights.</td></tr>
    <tr><td>Needle Engine</td><td><code>engine/*.dll</code></td><td>Provides the native libraries required by the transcription engine.</td></tr>
  </tbody>
</table>

<h3>Automatic Setup</h3>
<p>On startup, the application checks for the model and engine libraries next to the executable.</p>
<ul>
  <li>If both are available, the application configures Needle to use the local files and enables offline mode.</li>
  <li>If they are missing, it attempts to:
    <ol>
      <li>Check the Needle cache for previously downloaded files.</li>
      <li>Copy available model and engine files into the application directory.</li>
      <li>If necessary, trigger a download through Needle.</li>
      <li>Save the downloaded files locally for future use.</li>
    </ol>
  </li>
</ul>
<p>The initial download is approximately <strong>20 MB</strong> and requires an internet connection.</p>

<h3>Offline Mode</h3>
<p>Once the model and engine files are available in the application directory, transcription can run without an internet connection.</p>
<p>The application sets the following environment variables:</p>
<ul>
  <li><code>NEEDLE_WHISTLE_WEIGHTS</code>: Path to the local Whistle model.</li>
  <li><code>NEEDLE3_LIB_PATH</code>: Path to the local Needle engine DLL.</li>
  <li><code>NEEDLE_TELEMETRY=0</code>: Disables Needle telemetry.</li>
  <li><code>DO_NOT_TRACK=1</code>: Disables tracking signals.</li>
  <li><code>HF_HUB_OFFLINE=1</code>: Enables offline Hugging Face Hub operation when local resources are present.</li>
</ul>

<h2>Using the Application</h2>

<h3>1. Select an Audio File</h3>
<p>Click <strong>Browse</strong> next to the <strong>Audio file</strong> field and select a <code>.wav</code> file.</p>
<p>The application supports:</p>
<ul>
  <li>8-bit PCM WAV</li>
  <li>16-bit PCM WAV</li>
  <li>32-bit PCM WAV</li>
  <li>Mono and multi-channel audio</li>
  <li>Different sample rates (automatically resampled to 16 kHz)</li>
</ul>

<h3>2. Record Audio</h3>
<p>Alternatively, click <strong>Record</strong> to capture audio from your microphone.</p>
<p>When finished, click <strong>Stop</strong>.</p>
<p>The recording is automatically saved in:</p>
<pre><code>Documents/
└── WajeehaTranscribe/
    └── recording_YYYYMMDD_HHMMSS.wav
</code></pre>
<p>The recorded audio is automatically selected as the input file.</p>

<h3>3. Choose the Output Location</h3>
<p>Click <strong>Browse</strong> next to <strong>Save transcript to</strong> and select the destination for the transcript.</p>
<p>The output is saved as a <code>.txt</code> file.</p>
<p>If no output path is specified automatically, select one before starting transcription.</p>

<h3>4. Run Transcription</h3>
<p>Click <strong>Run transcription</strong>.</p>
<p>The status panel displays the current operation, including:</p>
<ul>
  <li>Audio loading</li>
  <li>Audio duration and number of chunks</li>
  <li>Model initialization</li>
  <li>Transcription progress</li>
  <li>Completion status</li>
  <li>Errors, if any</li>
</ul>
<p>When transcription finishes, the generated text is saved to the selected location.</p>

<h2>Audio Processing Details</h2>
<p>The Whistle model expects audio in the following format:</p>
<table>
  <thead>
    <tr><th>Property</th><th>Value</th></tr>
  </thead>
  <tbody>
    <tr><td>Sample Rate</td><td>16,000 Hz</td></tr>
    <tr><td>Channels</td><td>Mono</td></tr>
    <tr><td>Internal Format</td><td>16-bit PCM WAV</td></tr>
    <tr><td>Maximum Chunk Duration</td><td>Approximately 28 seconds</td></tr>
    <tr><td>Model Limit</td><td>30 seconds</td></tr>
  </tbody>
</table>

<h3>Automatic Audio Splitting</h3>
<p>Audio longer than 28 seconds is automatically split into smaller pieces.</p>
<p>Instead of cutting audio at an arbitrary point, the application searches for a relatively quiet section within the final 3 seconds of each chunk.</p>
<p>It then places the split near the quietest 100 ms interval.</p>
<p>This helps reduce the likelihood of cutting through spoken words.</p>
<p>After processing, all chunk transcripts are combined into a single text output.</p>
<blockquote>
  <p><strong>Recommendation:</strong> Although longer audio files are supported, shorter recordings (under 30 seconds) generally provide the most reliable results.</p>
</blockquote>

<h2>Dependencies</h2>
<p>The project uses the following Python libraries and components:</p>
<table>
  <thead>
    <tr><th>Dependency</th><th>Purpose</th></tr>
  </thead>
  <tbody>
    <tr><td><code>tkinter</code></td><td>Desktop graphical user interface</td></tr>
    <tr><td><code>numpy</code></td><td>Audio data processing</td></tr>
    <tr><td><code>soxr</code></td><td>Audio resampling</td></tr>
    <tr><td><code>sounddevice</code></td><td>Microphone recording</td></tr>
    <tr><td><code>needle</code></td><td>Cactus Whistle speech-to-text engine</td></tr>
    <tr><td><code>PyInstaller</code></td><td>Packaging the application into a Windows executable</td></tr>
  </tbody>
</table>
<p>The exact dependency versions are maintained in <code>requirements.txt</code>.</p>
<p>Install them using:</p>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Some dependencies may require additional native libraries or Windows audio-device support.</p>

<h2>Troubleshooting</h2>

<h3>Model or Engine Not Found</h3>
<p><strong>Problem:</strong> The application cannot find <code>whistle.cact</code> or the Needle engine DLL.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Check that <code>models/whistle.cact</code> exists.</li>
  <li>Check that the <code>engine</code> directory contains at least one DLL.</li>
  <li>Ensure the application has permission to access its directory.</li>
  <li>Connect to the internet and restart the application if the initial download is required.</li>
</ul>

<h3>Microphone Error</h3>
<p><strong>Problem:</strong> Recording cannot start.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Make sure a microphone is connected.</li>
  <li>Check Windows microphone privacy settings.</li>
  <li>Ensure the microphone is not exclusively occupied by another application.</li>
  <li>Verify that <code>sounddevice</code> is installed correctly.</li>
</ul>

<h3>Unsupported WAV Format</h3>
<p><strong>Problem:</strong> The application reports an unsupported WAV bit depth.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Convert the audio to PCM WAV using 8-bit, 16-bit, or 32-bit samples.</li>
  <li>For best compatibility, use 16-bit PCM WAV.</li>
</ul>

<h3>Transcription Fails</h3>
<p><strong>Problem:</strong> The transcription process fails or produces unexpected results.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Try a shorter audio file.</li>
  <li>Prefer clear recordings with minimal background noise.</li>
  <li>Use 16-bit PCM WAV.</li>
  <li>Ensure the model and engine files are present.</li>
  <li>Check the status panel for the reported error.</li>
</ul>

<h3>No Speech Detected</h3>
<p><strong>Problem:</strong> The output file is empty or contains no recognized speech.</p>
<p><strong>Solution:</strong></p>
<ul>
  <li>Ensure the recording contains audible speech.</li>
  <li>Check the microphone input level.</li>
  <li>Reduce background noise.</li>
  <li>Try recording again in a quieter environment.</li>
</ul>

<h2>Privacy</h2>
<p>Wajeeha Transcribe is designed to support local transcription.</p>
<p>After the model and engine have been downloaded and stored locally, audio processing can take place offline.</p>
<p>The application also disables Needle telemetry and tracking-related environment settings.</p>
<p>Microphone recordings are saved locally in the user's Documents folder, and transcripts are saved to the location selected by the user.</p>

<h2>Limitations</h2>
<ul>
  <li>WAV files are the supported input format.</li>
  <li>Only 8-bit, 16-bit, and 32-bit PCM WAV audio is supported.</li>
  <li>Audio is internally converted to 16 kHz mono.</li>
  <li>The Whistle model has a 30-second input limit, so longer recordings must be split.</li>
  <li>Transcription quality depends on recording clarity, background noise, and speech quality.</li>
  <li>Initial model setup requires internet access unless the required model and engine files are already available.</li>
</ul>

<h2>License</h2>
<p>MIT</p>

<hr>
<p><strong>Wajeeha Transcribe</strong> — Simple, local, and convenient speech-to-text transcription for Windows.</p>
