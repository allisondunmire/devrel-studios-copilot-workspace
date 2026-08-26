# Teams NDI Tech Check Template

## Subject

`TECH CHECK / {{Event Name}}: {{Session Name}} (Virtual via Teams NDI)`

## Location

`{{Teams Join URL}}`

## Online meeting

- Set `isOnlineMeeting` to `true`.
- Set `onlineMeetingProvider` to `teamsForBusiness`.
- Use the generated `onlineMeeting.joinUrl` as `{{Teams Join URL}}`.

## HTML body

```html
<p><strong>***** This email is generated from a service account that is not regularly monitored. For rescheduling or questions, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> *****</strong></p>

<p><strong>IMPORTANT INFORMATION - PLEASE READ THOROUGHLY:</strong></p>

<p>Review the Speaker Readiness guide and setup instructions below, and come prepared with your demo, slides, or presentation (if applicable).</p>

<p>During this tech check, we will:</p>
<ul>
  <li>Review technical details, including camera angles, audio, lighting, video playback needs, and screen sharing.</li>
  <li>Test your demo or presentation and run through the production and transitions.</li>
  <li>Ensure that your screen share is in the right format and accessible.</li>
  <li>Review what to expect on the day of the event in the 20 minutes prior to your session start time.</li>
  <li>Answer any questions you have about your session.</li>
</ul>

<p><strong>Details:</strong></p>
<table>
  <tr><td><strong>Event</strong></td><td>{{Event Name}}</td></tr>
  <tr><td><strong>Session title</strong></td><td>{{Session Name}}</td></tr>
  <tr><td><strong>Presenter(s)</strong></td><td>{{Presenter(s)}}</td></tr>
  <tr><td><strong>Location</strong></td><td>Teams</td></tr>
  <tr><td><strong>Show Owner</strong></td><td>{{Show Owner}}</td></tr>
  <tr><td><strong>Executive Producer</strong></td><td>{{Executive Producer}}</td></tr>
  <tr><td><strong>Technical Director</strong></td><td>{{Technical Director}}</td></tr>
</table>

<p><strong>ADO project:</strong></p>
<ul>
  <li><a href="{{ADO Project URL}}">{{ADO Project Label}}</a></li>
  <li>Need access? <strong>CoreIdentity Entitlements for ADO access:</strong> <a href="https://coreidentity.microsoft.com/manage/Entitlement/entitlement/studiosadopr-gyl1">Studios ADO Entitlement</a></li>
</ul>

<p><strong>Setup instructions:</strong></p>
<ul>
  <li>Set your screen resolution to 1920x1080.</li>
  <li>Set your scale to 125%: System &gt; Display &gt; Scale &amp; layout.</li>
  <li>Turn off the clock:
    <ul>
      <li>For PCs: Settings &gt; Time &amp; Language &gt; Date &amp; Time &gt; toggle off &ldquo;Show time and date in the System tray.&rdquo;</li>
      <li>For Macs: Open the Date &amp; Time panel, select &ldquo;Clock&rdquo; in the menu bar, go to the Clock tab, and uncheck &ldquo;Show date and time in menu bar.&rdquo;</li>
    </ul>
  </li>
  <li>If you are showing anything in the Azure portal, use <a href="https://github.com/microsoft/cloudcloak">Cloudcloak</a> to mask sensitive information.</li>
  <li>Embed pre-recorded video demos into your PowerPoint presentation, if you are using them.</li>
  <li>Remote video production utilizes a large amount of internet bandwidth. Other devices and applications on your network will impact your audio and video quality. Please plan your environment and any live demos accordingly.</li>
  <li>If you are not a Microsoft employee, please sign the <a href="https://aka.ms/releaseforms">release form</a>.</li>
</ul>

<p><strong>Video &amp; Audio</strong></p>

<p><strong>Set up:</strong></p>
<ul>
  <li>Choose a quiet location with great internet connectivity, <strong>preferably hard wired</strong>, and free from noise from pets or children.</li>
  <li>If you are on a network shared with others in your household, ensure others are not using the network at the time of recording.</li>
  <li>Set up your device horizontally with an HD camera and HD microphone, if possible.</li>
  <li>Camera height should be at or above eyeline. Prop up your device if needed using books, a tripod, or similar support.</li>
  <li>Keep your device horizontal.</li>
  <li>Situate yourself roughly 3-4 feet away from the video input.</li>
  <li>Look directly into the camera; try not to look at the interviewer or yourself.</li>
</ul>

<p><strong>Lighting:</strong></p>
<ul>
  <li>Make sure there is an adequate amount of light hitting your face directly. Natural lighting, such as a window, is best. Desk lamps can be a good alternative.</li>
  <li>Turn off or avoid any light sources behind you, such as a window.</li>
</ul>

<p><strong>Background:</strong></p>
<ul>
  <li>Consider background framing. Set up a nice background free of distractions. Avoid complicated or busy backgrounds and copyrighted images, items, or logos. No virtual or blurred backgrounds, please.</li>
</ul>

<p><strong>Audio:</strong></p>
<ul>
  <li>If possible, use an HD microphone or wear high-quality wireless headphones or a headset with a microphone. Earbud-style headphones such as AirPods work well because they do not distract in the shot.</li>
  <li>Silence cell phones and other devices, including computer notification sounds, to ensure they do not interrupt.</li>
  <li>Avoid empty rooms or rooms with high ceilings that can cause an echo, and avoid high-traffic areas.</li>
  <li>If using a mobile device, use something to stabilize it.</li>
</ul>
```

## Placeholder rules

- Replace every placeholder; never leave sample event, session, or presenter values in a rendered invitation.
- HTML-escape all workbook and user-provided values before insertion.
- Use the event-level values from the current workbook or ask the user when they are absent.
- The appointment start and end are the confirmed tech-check times. Do not derive them from the live-session buffer rules.
- Do not invent or reuse a Teams URL. Read the URL from the newly created event's `onlineMeeting.joinUrl`.
