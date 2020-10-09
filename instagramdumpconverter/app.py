import sys
import getopt
import os
import json
import uuid
import ntpath
import shutil
from datetime import datetime

def usage():
    print('python -m instagramdumpconverter -i <inputdir>')


def path_leaf(path):
    head, tail = ntpath.split(path)
    return ntpath.basename(head) or tail


def parseTime(timeString):
    result = None
    format1 = "%Y-%m-%dT%H:%M:%S.%f%z"
    format2 = "%Y-%m-%dT%H:%M:%S%z"
    try:
        result = datetime.strptime(timeString, format1)
    except ValueError:
        result = None
    try:
        result = datetime.strptime(timeString, format2)
    except ValueError:
        result = None
    return result


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


carouselStart = '''<div id="%s" class="carousel slide" data-ride="carousel">
<div class="carousel-inner">
'''
carouselImage = '''<div class="carousel-item%s">
    <img class="d-block w-100" src="%s" alt="%s">
</div>'''
carouselEnd = '''</div>
    <a class="carousel-control-prev" href="#%s" role="button" data-slide="prev">
        <span class="carousel-control-prev-icon" aria-hidden="true"></span>
        <span class="sr-only">Previous</span>
    </a>
    <a class="carousel-control-next" href="#%s" role="button" data-slide="next">
        <span class="carousel-control-next-icon" aria-hidden="true"></span>
        <span class="sr-only">Next</span>
    </a>
</div>
'''

workingDir = "%s%s" % (os.getcwd(), os.path.sep)

def run(argv):
    #Process the command line arguments
    input_dir = None
    verbose = False
    try:
        opts, args = getopt.getopt(argv, "hi:v", ["inputdir="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-i", "--inputdir"):
            input_dir = arg
        elif opt == "-v":
            verbose = True
        else:
            assert False, "unhandled option"
    argError = False
    if input_dir is None:
        argError = True
        print("No input directory specified")
    if argError:
        usage()
        sys.exit(2)
    print("Processing data in %s" % (input_dir))

    #make sure the input path exists
    if not os.path.isdir(input_dir):
        print("Unable to find input_dir '%s'" % input_dir)
        sys.exit(3)

    mediaFiles = []
    #Go through the directory tree looking for media.json
    for subdir, dirs, files in os.walk(input_dir):
        for file in files:
            if (file == "media.json"):
                list.append(mediaFiles, os.path.join(subdir, file))

    htmlPost = ""
    #Keep a list of hashes. Posts that have multiple images have the same timestamp and caption
    postHash = {}
    for filename in mediaFiles:
        print("Opening media file %s" % filename)
        with open(filename) as f:
            file_data = json.load(f)
        print("Processing json data")
        for post_type in file_data.keys():
            print("Processing %s" % post_type)
            for post in file_data[post_type]:
                if len(post.keys()) > 0:
                    path = post.get('path', None)
                    if path is not None:
                        fullPath = "%s/%s" % (path_leaf(filename), path)
                        post['path'] = fullPath

                    taken_at = post.get('taken_at', "")
                    dt_taken_at = parseTime(taken_at)
                    post['taken_at'] = dt_taken_at.strftime("%B %d, %Y") if dt_taken_at is not None else ""
                    hash_taken_at = dt_taken_at.strftime("%Y-%m-%d %H:%M") if dt_taken_at is not None else ""

                    if hash_taken_at not in postHash:
                        postHash[hash_taken_at] = []
                    postHash[hash_taken_at].append(post)

    #process the post hash
    for post_date in postHash.keys():
        postDetails = "<div class='blog-post'><p class='blog-post-meta'>%s</p>" % taken_at
        if len(postHash[post_date]) == 1:
            post = postHash[post_date][0]
            caption = post.get('caption', "")
            taken_at = post.get('taken_at', "")
            path = post.get('path', None)

            if path is not None:
                if os.path.isfile("%s%s" % (input_dir, path.replace("/", os.path.sep))):
                    mediaHtml = "<img src='%s' class='img-fluid' alt='%s'>" % (path, caption)
                    if fullPath.endswith("mp4"):
                        mediaHtml = "<div class='embed-responsive embed-responsive-16by9'><video width='320' height='240' controls><source src='%s' type='video/mp4'></video></div>" % fullPath
                    postDetails = "%s%s" % (postDetails, mediaHtml)
                else:
                    print("ERROR: Unable to find file at %s" % ("%s%s" % (input_dir, path.replace("/", os.path.sep))))
        else:
            uid = uuid.uuid4().hex
            postDetails = "%s\n%s" % (postDetails, carouselStart % uid)
            count = 0
            videoPosts = []
            for post in postHash[post_date]:
                caption = post.get('caption', "")
                taken_at = post.get('taken_at', "")
                path = post.get('path', None)

                if path is not None:
                    if os.path.isfile("%s%s" % (input_dir, path.replace("/", os.path.sep))):
                        if path.endswith("mp4"):
                            videoPosts.append(post);
                        else:
                            mediaHtml = carouselImage % (" active" if count == 0 else "", path, caption)
                        postDetails = "%s\n%s" % (postDetails, mediaHtml)
                        count += 1
                    else:
                        print("ERROR: Unable to find file at %s" % ("%s%s" % (input_dir, path.replace("/", os.path.sep))))
            postDetails = "%s\n%s" % (postDetails, carouselEnd % (uid, uid))
            #add videos as separate posts since they can't be in the carousel
            for post in videoPosts:
                postDetails = "%s<div class='embed-responsive embed-responsive-16by9'><video width='320' height='240' controls><source src='%s' type='video/mp4'></video></div>" % (postDetails, fullPath)
        postDetails = "%s<blockquote><p>%s</p><blockquote></div>" % (postDetails, caption)
        htmlPost = "%s%s" % (htmlPost, postDetails)

    #Read in the template file
    file = open("webtemplate/index.html")
    htmlTemplate = file.read()
    file.close()
    #Replace place holders
    htmlTemplate = htmlTemplate.replace("%%HEADER%%", "")
    htmlTemplate = htmlTemplate.replace("%%POSTS%%", htmlPost)
    htmlTemplate = htmlTemplate.replace("%%FOOTER%%", "")

    #copy css and js files to inputDir and write out htmlTemplate to index.html
    templateDir = "%s%s" % ("webtemplate", os.path.sep)

    srcDir = "%s%s" % (workingDir, "%s%s" % (templateDir, "css"))
    outputDir = "%s%s" % (input_dir, "css")
    shutil.rmtree(outputDir)
    os.mkdir(outputDir)
    copytree(srcDir, outputDir)

    srcDir = "%s%s" % (workingDir, "%s%s" % (templateDir, "js"))
    outputDir = "%s%s" % (input_dir, "js")
    shutil.rmtree(outputDir)
    os.mkdir(outputDir)
    copytree(srcDir, outputDir)

    srcDir = "%s%s" % (workingDir, "%s%s" % (templateDir, "blog.css"))
    outputDir = "%s%s" % (input_dir, "blog.css")
    shutil.copyfile(srcDir, outputDir)

    #write the html file
    file = open("%s%s" % (input_dir,  "index.html"), "w")
    file.write(htmlTemplate)
    file.close()