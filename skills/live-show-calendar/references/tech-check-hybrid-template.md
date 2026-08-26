# Hybrid Tech Check Template

## Subject

`TECH CHECK / {{Event Name}}: {{Session Name}} (Mandatory Tech Check - Hybrid: In Studio *AND* Teams NDI)`

The asterisks around `AND` are literal because Outlook subjects do not support rich-text emphasis.

## Location

`DevRel Studios - Microsoft Building 25 (15700 NE 39th St, Redmond, WA 98052); 25/1332 (for in-studio presenters) and Teams NDI (for remote presenters)`

## Online meeting

- Set `isOnlineMeeting` to `true`.
- Set `onlineMeetingProvider` to `teamsForBusiness`.
- Use the generated `onlineMeeting.joinUrl` for remote presenters. Do not replace the combined physical/remote Location text with the URL.

## HTML body

```html
<p><strong>***** This email is generated from a service account that is not regularly monitored. For rescheduling or questions, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> *****</strong></p>

<p><strong>IMPORTANT INFORMATION - PLEASE READ THOROUGHLY:</strong></p>

<p>This mandatory rehearsal and tech check is your chance to make sure that you know everything you need to know for your talk and the event and that all technical aspects are in order.</p>

<p><strong>FOR IN-PERSON PRESENTERS:</strong></p>
<p><strong><em>Please be sure to arrive at the studio at least 15 minutes prior to your rehearsal and tech check time.</em></strong></p>
<p>Review the Speaker Readiness guide and setup instructions below, and come prepared with your demo, slides, or presentation (if applicable). During this rehearsal and tech check, we will:</p>
<ul>
  <li>Review technical details, including computer signal, font sizes, resolution and aspect ratio, video/audio integration and playback needs, and screen-share format and accessibility.</li>
  <li>Test your demo or presentation and run through the production and transitions.</li>
  <li>Review what to expect on the day of the event regarding transitions between sessions.</li>
  <li>Answer any questions you have about your session.</li>
  <li>If your session needs any audio to come from your computer, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a>.</li>
</ul>

<p><strong>FOR REMOTE PRESENTERS VIA TEAMS NDI:</strong></p>
<p><strong><em>Please join the Teams meeting at the start of your rehearsal and tech check time. The schedule is very tight, so it is important that remote presenters arrive on time.</em></strong></p>
<p>Review the Speaker Readiness guide and setup instructions below, and come prepared with your demo, slides, or presentation (if applicable). During this tech check, we will:</p>
<ul>
  <li>Review technical details, including camera angles, audio, lighting, video playback needs, and screen sharing.</li>
  <li>Test your demo or presentation and run through the production and transitions.</li>
  <li>Ensure that your screen share is in the right format and accessible.</li>
  <li>Review what to expect on the day of the event in the 20 minutes prior to your session start time.</li>
  <li>Answer any questions you have about your session.</li>
</ul>

<p><strong>If you have an unmovable conflict, please contact <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> as soon as possible.</strong></p>

<p><strong>Details:</strong></p>
<table>
  <tr><td><strong>Event</strong></td><td>{{Event Name}}</td></tr>
  <tr><td><strong>Session title</strong></td><td>{{Session Name}}</td></tr>
  <tr><td><strong>In-person presenter(s)</strong></td><td>{{In-Person Presenter(s)}}</td></tr>
  <tr><td><strong>Remote presenter(s)</strong></td><td>{{Remote Presenter(s)}}</td></tr>
  <tr><td><strong>Location</strong></td><td>DevRel Studios | 25/1332: Studio (for in-person presenters) &amp; Teams NDI (for remote presenters)</td></tr>
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

<p><strong>Wardrobe</strong></p>
<p><strong>Don&rsquo;t:</strong></p>
<ul>
  <li>Wear large-logo shirts or non-Microsoft logos unless related to your technology topic.</li>
  <li>Wear shirts with a busy print or tight pattern.</li>
  <li>Wear solid black, solid white, or any green.</li>
  <li>Wear hats unless worn for religious observance.</li>
</ul>

<p><strong>Do:</strong></p>
<ul>
  <li>Wear color. Muted colors are fine; color is always good on camera.</li>
  <li>Ensure your clothes are wrinkle free; HD catches everything.</li>
  <li>Wear simple jewelry, or none. Large jewelry can be distracting and create additional noise.</li>
</ul>

<p><strong>Directions:</strong></p>
<p>
  <strong>Microsoft Building 25</strong><br>
  15700 NE 39th St<br>
  Redmond, WA 98052
</p>

<p>DevRel Studios (formerly the Ch9 Studio) is located in Building 25, Room 1332.</p>
<ul>
  <li>Building 25 has a north and south wing. DevRel Studios is in the south wing, toward the left as you are facing the front of Building 25.</li>
  <li>If you are not a vendor or FTE, allow time to check in at reception.</li>
  <li>The sponsor for reception to contact by email upon your arrival is {{Technical Director}}. They will meet you in the lobby after you are checked in.</li>
  <li>FTEs and vendors can register their vehicles for on-site parking in advance at <a href="https://parking.microsoft.com/">parking.microsoft.com</a>.</li>
</ul>
```

## Placeholder rules

- Replace every placeholder; never leave sample event, session, presenter, or production-role values in a rendered invitation.
- HTML-escape all workbook and user-provided values before insertion.
- Use event-level values from the current workbook or ask the user when they are absent.
- Parse `In-Person Presenter(s)` and `Remote Presenter(s)` from the labeled `Presenter(s)` source value according to the skill rules.
- Require at least one in-person presenter and one remote presenter.
- The appointment start and end are the confirmed tech-check times. Do not derive them from the live-session buffer rules.
- Do not invent or reuse a Teams URL. Read it from the newly created event's `onlineMeeting.joinUrl`.
- Do not include vaccination or other access requirements unless they are verified against current studio policy for that event.
