# In Studio Appointment Template

## Subject

`{{Event Name}} | Session: {{Session Name}} (In-studio livestream session)`

## HTML body

```html
<p><strong>***** This email is generated from a service account that is not regularly monitored. For rescheduling or questions, please email <a href="mailto:v-adunmire@microsoft.com">v-adunmire@microsoft.com</a> *****</strong></p>

<p><strong>IMPORTANT SHOOT INFORMATION - PLEASE READ THOROUGHLY:</strong></p>
<ul>
  <li>This event will be streaming live with presenters <strong>in person</strong> in the DevRel studio space.</li>
  <li><strong>Call Times for Presenters are listed below. <em>Be sure to arrive at the studio 30 minutes prior to your live session start time.</em></strong></li>
  <li>See below for directions and building access information.</li>
  <li>Please come prepared with your demo, slides, or presentation (if applicable).</li>
</ul>

<p><strong>Details:</strong></p>
<table>
  <tr><td><strong>Event</strong></td><td>{{Event Name}}</td></tr>
  <tr><td><strong>Session title</strong></td><td>{{Session Name}}</td></tr>
  <tr><td><strong>Presenter(s)</strong></td><td>{{Presenter(s)}}</td></tr>
  <tr><td><strong>Presenter(s) Call time</strong></td><td>{{Appointment Start Time}}</td></tr>
  <tr><td><strong>Session start time</strong></td><td>{{Session Start Time}}</td></tr>
  <tr><td><strong>Location</strong></td><td>DevRel Studios - Microsoft Building 25 (15700 NE 39th St, Redmond, WA 98052); 25/1332</td></tr>
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

<p><strong>Setup instructions (if you plan to share your screen):</strong></p>
<ul>
  <li>Set your screen resolution to 1920x1080.</li>
  <li>Set your scale to 125%: System &gt; Display &gt; Scale &amp; layout.</li>
  <li>Turn off the clock:
    <ul>
      <li>For PCs: Settings &gt; Time &amp; Language &gt; Date &amp; Time &gt; Toggle &ldquo;Show time and date in the System tray.&rdquo;</li>
      <li>For Macs: Open the Date &amp; Time panel, select &ldquo;Clock&rdquo; in the menu bar, go to the Clock tab, and uncheck &ldquo;Show date and time in menu bar.&rdquo;</li>
    </ul>
  </li>
  <li>If you are showing anything in the Azure portal, use <a href="https://github.com/microsoft/cloudcloak">Cloudcloak</a> to mask sensitive information.</li>
  <li>Embed pre-recorded video demos into your PowerPoint presentation, if you are using them.</li>
  <li>Remote video production utilizes a large amount of internet bandwidth. Other devices and applications on your network will impact your audio and video quality. Please plan your environment and any live demos accordingly.</li>
  <li>If you are not a Microsoft employee, please sign the <a href="https://aka.ms/releaseforms">release form</a>.</li>
</ul>

<p><strong>Wardrobe Tips</strong></p>
<p><strong>Do:</strong></p>
<ul>
  <li>Wear color. Muted colors are fine; color is always good on camera.</li>
  <li>Ensure your clothes are wrinkle free; HD catches everything.</li>
  <li>Wear simple jewelry, or none. Large jewelry can be distracting and create additional noise.</li>
</ul>

<p><strong>Don&rsquo;t:</strong></p>
<ul>
  <li>Wear large-logo shirts or non-Microsoft logos unless related to your technology topic.</li>
  <li>Wear shirts with a busy print or tight pattern.</li>
  <li>Wear solid black, solid white, or any green.</li>
  <li>Wear hats unless worn for religious observance.</li>
</ul>

<p><strong>Directions</strong></p>
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
```

## Placeholder rules

- HTML-escape all workbook values before insertion.
- Render appointment and session times in Pacific Time using a readable 12-hour format such as `8:30 AM PT`.