# In Studio Tech Check Template

## Subject

`TECH CHECK / {{Event Name}}: {{Session Name}} (Mandatory studio tech check - in person)`

## Location

`DevRel Studios - Microsoft Building 25 (15700 NE 39th St, Redmond, WA 98052); 25/1332`

## HTML body

```html
<p><strong>***** This email is generated from a service account that is not regularly monitored. For rescheduling or questions, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> *****</strong></p>

<p><strong>IMPORTANT INFORMATION - PLEASE READ THOROUGHLY:</strong></p>

<p>This mandatory tech check is required to make sure that all technical aspects are in order for your session and the event.</p>

<p><strong><em>Please be sure to arrive at the studio at least 15 minutes prior to your tech check time.</em></strong></p>

<p>Review the Speaker Readiness guide and setup instructions below, and come prepared with your demo, slides, or presentation (if applicable).</p>

<p>During this rehearsal and tech check, we will:</p>
<ul>
  <li>Review technical details, including computer signal, font sizes, resolution and aspect ratio, video/audio integration and playback needs, and screen-share format and accessibility.</li>
  <li>Test your demo or presentation and run through the production and transitions.</li>
  <li>Review what to expect on the day of the event regarding transitions between sessions.</li>
  <li>Answer any questions you have about your session.</li>
</ul>

<p><strong>If you have an unmovable conflict, please contact <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> as soon as possible.</strong></p>

<p><strong>Details:</strong></p>
<table>
  <tr><td><strong>Event</strong></td><td>{{Event Name}}</td></tr>
  <tr><td><strong>Session title</strong></td><td>{{Session Name}}</td></tr>
  <tr><td><strong>Presenter(s)</strong></td><td>{{Presenter(s)}}</td></tr>
  <tr><td><strong>Location</strong></td><td>DevRel Studios | Building 25/Room 1332</td></tr>
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
  <li>Remote video production utilizes a large amount of internet bandwidth. Other devices and applications on your network will impact your audio and video quality. Please plan your environment and any live demos accordingly.</li>
  <li>If you are not a Microsoft employee, please sign the <a href="https://aka.ms/releaseforms">release form</a>.</li>
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

- Replace every placeholder; never leave sample event, session, or presenter values in a rendered invitation.
- HTML-escape all workbook and user-provided values before insertion.
- Use the event-level values from the current workbook or ask the user when they are absent.
- The appointment start and end are the confirmed tech-check times. Do not derive them from the live-session buffer rules.
