# Instagram Dump Converter 
Instagram allows you to export your data from your account using the instructions here https://help.latest.instagram.com/181231772500920?helpref=related 

This project is python code that will easily convert the data dump into HTML so it can be printed or easily viewed. Please note, the only data that this handles is your initial description and the image or video. Comments are downloaded in the data files but there is no way to associate the comments with its post.

#How To Use

**Instagram has added an HTML option when downloading. This is a great option but if you want to download and process with this system make sure to choose JSON as the download option.
<ol>
<li>Request your data download from Instagram using the instructions <a href="https://help.latest.instagram.com/181231772500920?helpref=related">https://help.latest.instagram.com/181231772500920?helpref=related</a></li>
<li>Wait for the email telling you that your download is ready</li>
<li>Click the link in the email</li>
<li>Login to Instagram</li>
<li>Download all of the files associated with your data export.
<ul>
<li>I do not regularly post to Instagram and mine was 4 zip files.</li>
</ul>
</li>
<li>Copy all of the zip files into a new directory</li>
<li>Unzip all of the files into their own directory
<ul><li>This is important because each zip file that contains images/videos will contain a file named media.json that will be overwritten.</li></ul></li>
<li>Run Instagram Dump Converter using the directory you created in step 6 above as the input directory.</li>
</ol>