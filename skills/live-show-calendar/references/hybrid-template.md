# Hybrid Appointment Template

## Subject

`{{Event Name}} | Session: {{Session Name}} ((Hybrid session: In Studio *AND* Teams NDI))`

The asterisks around `AND` are literal because Outlook subjects do not support rich-text emphasis.

## HTML body

```html
<div style="font-family:Calibri,Arial,sans-serif;font-size:11pt;color:#000000;line-height:1.2;">
<p style="margin:0 0 16px 0;padding:2px 6px;background-color:#d9d9d9;"><strong><em>** This email is generated from a service account that is not regularly monitored. For rescheduling or questions, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a>. **</em></strong></p>

<p style="margin:0 0 4px 0;"><strong>IMPORTANT INFORMATION - PLEASE READ THOROUGHLY:</strong></p>
<ul>
  <li>This LIVE session will be conducted with a presenter in the DevRel studio space and a presenter on Teams.</li>
  <li>Call Times for Presenters are listed below:
    <ul>
      <li><em>In-person presenters should arrive 30 minutes prior to the live session start time.</em></li>
      <li><em>Remote presenters should join the Teams call (LOGIN INFO AT BOTTOM OF THIS INVITE) 20 minutes prior to the live session start time.</em></li>
    </ul>
  </li>
  <li>See below for directions and building access information.</li>
  <li>Please come prepared with your demo, slides, or presentation (if applicable).</li>
</ul>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Shoot details:</strong></p>
<table role="presentation" border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;border:1px solid #000000;width:804px;max-width:100%;">
  <tr><td><strong>Event</strong></td><td>{{Event Name}}</td></tr>
  <tr><td><strong>Session title</strong></td><td>{{Session Name}}</td></tr>
  <tr><td><strong>Session number</strong></td><td>{{Session ID}}</td></tr>
  <tr><td><strong>In-person presenter(s)</strong></td><td>{{In-Person Presenter(s)}}</td></tr>
  <tr><td><strong>In-person call time</strong></td><td>{{Appointment Start Time}}</td></tr>
  <tr><td><strong>Remote presenter(s)</strong></td><td>{{Remote Presenter(s)}}</td></tr>
  <tr><td><strong>Remote call time</strong></td><td>{{Remote Call Time}}</td></tr>
  <tr><td><strong>Session start time</strong></td><td>{{Session Start Time}}</td></tr>
  <tr><td><strong>Session end time</strong></td><td>{{Session End Time}}</td></tr>
  <tr><td><strong>Session length</strong></td><td>{{Session Duration}}</td></tr>
  <tr><td><strong>In-person location</strong></td><td>DevRel Studios - Microsoft Building 25 (15700 NE 39th St, Redmond, WA 98052); 25/1332</td></tr>
  <tr><td><strong>Remote location</strong></td><td>Teams NDI</td></tr>
  <tr><td><strong>Show Owner</strong></td><td>{{Show Owner}}</td></tr>
  <tr><td><strong>Executive Producer</strong></td><td>{{Executive Producer}}</td></tr>
  <tr><td><strong>Technical Director</strong></td><td>{{Technical Director}}</td></tr>
</table>

<p><strong>ADO project:</strong></p>
<ul>
  <li><a href="{{ADO Project URL}}">{{ADO Project Label}}</a></li>
  <li>Need access? <strong>CoreIdentity Entitlements for ADO access:</strong> <a href="https://coreidentity.microsoft.com/manage/Entitlement/entitlement/studiosadopr-gyl1">Studios ADO Entitlement</a></li>
</ul>

<p><strong>Speaker readiness guides:</strong></p>
<ul>
  <li><a href="https://microsoft.sharepoint.com/:w:/t/MicrosoftDeveloperStudiosChannel9/ESd__4ZM1pxHilV8w0RRxowBAvNlBMG5SPIHso6dfYkIQQ?e=8cUkms">Speaker Readiness.docx</a></li>
  <li><a href="https://dev.azure.com/devrel/Studios/_wiki/wikis/Studios.wiki/6314/Speaker-readiness-for-presenters?anchor=live-presenters---remote">Speaker readiness for presenters - Overview</a></li>
</ul>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Live presenters - remote via Teams:</strong></p>
<ul>
  <li>Join the Teams call 20 minutes ahead of your live session start time. Someone from the production team will be with you shortly to check your screen share/video/audio.</li>
  <li>If multiple presenters, inform the Executive Producer (EP) or Technical Director (TD) who will be speaking first and who will be sharing the presentation and/or demo so we understand the flow of your session.</li>
  <li>At the start of your presentation, verbally introduce yourself with your full name and title and describe yourself for audiences with visual impairments. This gives the production team time to run a lower-third identifier bar at the bottom of the screen with your name/title. Remove any title/intro slides from your presentation since they will be redundant.</li>
  <li>The production team will be in touch with you in the Teams chat. Please make every attempt to use the entire time allotted for your session. Ending your session too early or late can be an issue for the next presenter after you.</li>
  <li>Provide verbal cues for your transitions. This lets your audience know what to expect; it also helps our production team know which computer to pull slides or demo from to share on screen. For example, if you have been presenting slides and intend to switch to your demo, say out loud, &ldquo;now I&rsquo;ll share the demo.&rdquo; Or, in the case of two presenters, &ldquo;that was my presentation; now Sally will share the demo.&rdquo;</li>
  <li>When you are wrapping up, provide a verbal cue such as &ldquo;I hope you enjoyed this session&rdquo; or &ldquo;Thank you very much; that&rsquo;s all the time I have.&rdquo; This helps our production crew and hosts (if applicable) prepare to make the transition to Q&amp;A or to the next session.</li>
  <li>Monitor the chat in Teams to view any notes/comments from the production team.</li>
  <li>When you are finished with your session/Q&amp;A, mute your microphone, keep your camera ON, and do not stop sharing your screen until given the all-clear from the production team. They will let you know when you are clear to exit the Teams call.</li>
</ul>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Setup instructions (if you plan to share your screen):</strong></p>
<ul>
  <li>Set your screen resolution to 1920x1080.</li>
  <li>Set your scale to 125%: System &gt; Display &gt; Scale &amp; layout.</li>
  <li>Turn off the clock:
    <ul>
      <li>For PCs: Settings &gt; Time &amp; Language &gt; Date &amp; Time &gt; Toggle &ldquo;Show time and date in the System tray.&rdquo;</li>
      <li>For Macs: Open the Date &amp; Time panel, select &ldquo;Clock&rdquo; in the menu bar, go to the Clock tab, and uncheck &ldquo;Show date and time in menu bar.&rdquo;</li>
    </ul>
  </li>
  <li>If you are showing anything in the Azure portal, use the <a href="https://github.com/clarkio/azure-mask/releases/download/1.1.8/azure-mask-1.1.8.zip">AZ Mask extension</a> to hide your subscription ID. This link downloads the extension package.</li>
  <li>Embed pre-recorded video demos into your PowerPoint presentation, if you are using them.</li>
  <li>Remote video production utilizes a large amount of internet bandwidth. Other devices and applications on your network will impact your audio and video quality. Please plan your environment and any live demos accordingly.</li>
  <li>If you are not a Microsoft employee, please sign the <a href="https://aka.ms/releaseforms">release form</a>.</li>
</ul>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Video &amp; Audio:</strong></p>
<p><strong>Set up:</strong></p>
<ul>
  <li>Choose a quiet location with great internet connectivity, preferably hard wired, free from noise from pets or children.</li>
  <li>If you are on a network shared with others in your household, please ensure others are not using the network at the time of recording.</li>
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
  <li>Consider background framing. Set up a nice background free of distractions. Avoid complicated or busy backgrounds, or any copyrighted images, items, or logos. No virtual or blurred backgrounds, please.</li>
</ul>

<p><strong>Audio:</strong></p>
<ul>
  <li>If possible, use an HD microphone or wear high-quality wireless headphones or a headset with a microphone. Earbud-style headphones such as AirPods work well because they do not distract in the shot.</li>
  <li>Silence cell phones and other devices, including computer notification sounds, to ensure they do not interrupt.</li>
  <li>Avoid empty rooms or rooms with high ceilings that can cause an echo, and avoid high-traffic areas.</li>
  <li>If using a mobile device, use something to stabilize it.</li>
</ul>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Wardrobe tips</strong></p>
<p>Avoid large logos, busy or tight patterns, solid black or white, and hats unless worn for religious observance. Wear color, wrinkle-free clothing, and simple jewelry.</p>

<p style="margin:18px 0 4px 0;color:#2f5597;font-size:14pt;"><strong>Directions:</strong></p>
<p>
  Microsoft Building 25<br>
  15700 NE 39th St<br>
  Redmond, WA 98052
</p>

<p><strong>DevRel Studios</strong> (formerly the Ch9 Studio) is located in Building 25, Room 1332.</p>
<ul>
  <li>Building 25 has a north and south wing. DevRel Studios is in the south wing, toward the left as you are facing the front of Building 25.</li>
  <li>If you are not a vendor or FTE, allow time to check in at reception.</li>
  <li>The sponsor for reception to contact by email upon your arrival is {{Technical Director}}. They will meet you in the lobby after you are checked in.</li>
  <li>FTEs and vendors can register their vehicles for on-site parking in advance at <a href="https://parking.microsoft.com/">parking.microsoft.com</a>.</li>
</ul>
<p style="margin:12px 0 0 0;"><img src="{{Floor Plan Image URL}}" alt="Floor plan showing the DevRel Studios location in Microsoft Building 25" width="640" style="display:block;width:640px;max-width:100%;height:auto;border:0;"></p>
</div>
```

## Placeholder rules

- HTML-escape all workbook and user-provided values before insertion.
- Render all call and session times in the confirmed event time zone using a readable 12-hour format such as `8:30 AM PT`.
- `Appointment Start Time` is 30 minutes before session start.
- `Remote Call Time` is 20 minutes before session start.
- Parse `In-Person Presenter(s)` and `Remote Presenter(s)` from the labeled `Presenter(s)` source value according to the skill rules.
- Apply the inline styles as written; do not replace them with CSS classes or a `<style>` block because
  Outlook desktop uses the Word HTML rendering engine.
- Render the floor-plan `<img>` only when `Floor Plan Image URL` is a confirmed HTTPS image URL.
  Remove the entire containing `<p>` when the URL is unavailable; never send the unresolved placeholder.