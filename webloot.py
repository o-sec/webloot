#!/usr/bin/python3

#
# author : o-sec - https://github.com/o-sec
#

import requests
import re
import sys


class DataCollector():

    #get the page source code
    def GetPageSource(self,url) -> str:
        headers = {
        "User-Agent" :"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chromium/81.0.9432.582 Safari/537.36"
        }

        try:
            response = requests.get(url,headers=headers,timeout=5)
            PageSource = response.text if response.status_code == 200 else None
            return PageSource

        except requests.exceptions.Timeout:
            pass
        except requests.exceptions.ConnectionError:
            pass
        except requests.exceptions.HTTPError:
            pass
        except requests.exceptions.RequestException:
            pass



    #extract subdomains from page source code
    def GetSubdomains(self,PageSource) -> list:
        try:
            subdomains =  [ re.split("%..",subdomain)[-1] for subdomain in re.findall(f"[^/\"'><]*\.{self.domain}", PageSource)]
            subdomains = set(subdomains)
            subdomains = list(subdomains)
            return subdomains
        except Exception as e:
            print(e)



    #extract links from page source code
    def GetLinks(self,PageSource) -> list :
        try:
            links = re.findall("https?://[^\s\"'><]+", PageSource)
            return links
        except Exception as e:
            print(e)




    #extract directories path from page source code
    def GetDirectories(self,PageSource) -> list:
        try:
            directories = [directory for directory in re.findall(r'(?:href|src)=["\']([^"\']+)(?:"|\')', PageSource)  if directory.endswith("/")]
        except Exception as e:
            print(e)





     #extract js files from page source code
    def GetJsFiles(self,PageSource) -> list:
        try:
            JsFiles = [JsFile for JsFile in re.findall(r'(?:href|src)=["\']([^"\']+)(?:"|\')', PageSource)  if JsFile.endswith(".js")]
            return JsFiles
        except Exception as e:
            print(e)



    #extract html comments from page source code
    def GetHtmlComments(self,PageSource) -> list:
        try:
            HtmlComments = re.findall(r'<!--.*?-->', PageSource)
            return HtmlComments
        except Exception as e:
            print(e)


    #extract email addresses from page source code
    def GetEmailAddresses(self,PageSource) -> list:
        try:
            EmailAddresses = re.findall("[a-zA-Z0-9._%+-]+@[^. ]+\.[^.><\"'\-+/&;:,%$#\!\^\*\(\) ]+", PageSource)
            return EmailAddresses
        except Exception as e:
            print(e)




class Webloot(DataCollector):

    def __init__(self,url):

        url = url[:-1] if url.endswith("/") else url
        self.domain = re.search("[^./]+\.[^.]+$",url).group()

        self.loot = {
           "subdomains" : [],
           "emails" : [],
           "links" : [],
           "jsFiles": {},
           "directories":{},
           "comments":{},
           }




    #collect loot ( subdomains | links | jsFiles | directories | html comments | email addresses).
    def CollectLoot(self,url,depth=1) -> None:

        print("="*60 +"\n")
        print(f"Target URL  : {url}\nDepth Level : {depth}\n")
        print("\n"+ "="*60 + "\n")
        print("[*] Collecting data...\n")

        #get the main page source code
        MainPageSource = self.GetPageSource(url)

        if not MainPageSource:
            print(f"Unable to connect to : {url} , Please verify the URL and your network connection.")
            exit()

        #collect links
        links = set(self.GetLinks(MainPageSource))
        self.loot["links"].extend(list(links))
        #collect subdomains
        subdomains = set(self.GetSubdomains(MainPageSource))
        self.loot["subdomains"].extend(list(subdomains))
        #collect email addresses
        emails = set(self.GetEmailAddresses(MainPageSource))
        self.loot["emails"].extend(list(emails))
        #collect directories
        directories = self.GetDirectories(MainPageSource)
        if directories:
            self.loot["directories"][url] = directories
        #collect jsFiles
        JsFiles = self.GetJsFiles(MainPageSource)
        if JsFiles:
            self.loot["jsFiles"][url] = JsFiles
        #collect HtmlComments
        HtmlComments = self.GetHtmlComments(MainPageSource)
        if HtmlComments:
            self.loot["comments"][url] = HtmlComments

        self.CollectExtraLoot(depth)



    #collect loot from sublinks and it's sublinks (based on depth level)
    # if depth=1 it will collect loot from sublinks of the main url.
    def CollectExtraLoot(self,depth) -> None:
        RoundsCounter = 0

        for _ in range(depth):
            RoundsCounter += 1
            #shallow copy of links list
            links = self.loot["links"][:]
            progress = 0

            for link in links:
                progress += 1
                try:
                    print(f" Depth {RoundsCounter}  |  Progress :   {int(progress * 100 / len(links))}%", end="\r")

                    if re.search(f"https?://[^/]*\.{self.domain}[^\s\"'>]+",link) and (link.endswith(".html") or link.endswith(".php")  or link.endswith("/")):
                        PageSource = self.GetPageSource(link)

                        if not PageSource:
                            continue

                        #collect sublinks
                        SubLinks = self.GetLinks(PageSource)
                        self.loot["links"].extend(SubLinks)
                        #collect subdomains
                        subdomains = self.GetSubdomains(PageSource)
                        self.loot["subdomains"].extend(subdomains)
                        #collect email addresses
                        emails = set(self.GetEmailAddresses(PageSource))
                        self.loot["emails"].extend(list(emails))
                        #collect directories
                        directories = self.GetDirectories(PageSource)
                        if directories:
                            self.loot["directories"][link] = directories
                        #collect js files
                        JsFiles = self.GetJsFiles(PageSource)
                        if JsFiles:
                            self.loot["jsFiles"][link] = JsFiles
                        #collect html comments
                        HtmlComments = self.GetHtmlComments(PageSource)
                        if HtmlComments:
                            self.loot["comments"][link] = HtmlComments

                except KeyboardInterrupt as ki:
                    print(f"Round {RoundsCounter} stoped ! , KeyboardInterrupt .")
                    break


            #cleaning the loot
            self.loot["links"] = set(self.loot["links"])
            self.loot["links"] = list(self.loot["links"])
            self.loot["subdomains"]  = set(self.loot["subdomains"])
            self.loot["subdomains"]  = list(self.loot["subdomains"])
            self.loot["emails"] = set(self.loot["emails"])
            self.loot["emails"] = list(self.loot["emails"])



    #display the collected data on screen
    def DisplayCollectedLoot(self) -> None:

        print("\n\n\n"+ "=" * 60)
        print("     Data Collection Summary ")
        print("=" * 60 +"\n")

        # Display Subdomains
        print("Subdomains Found:")
        if self.loot["subdomains"]:
            for subdomain in self.loot["subdomains"]:
                print(f"  - {subdomain.strip()}")
        else:
            print("  No subdomains found.")
        print("\n" + "=" * 60)

        # Display email addresses
        print("\nEmail addresses Found:")
        if self.loot["emails"]:
            for email in self.loot["emails"]:
                print(f"  - {email.strip()}")
        else:
            print("  No email addresses found.")
        print("\n" + "=" * 60)

        # Display Links
        print("\nLinks Found:")
        if self.loot["links"]:
            for link in self.loot["links"]:
                print(f"   - {link.strip()}")
        else:
            print("  No links found.")
        print("\n" + "=" * 60)

        # Display JavaScript Files
        print("\nJavaScript Files Discovered:")
        if self.loot["jsFiles"]:
            for SourceUrl, JsFiles in self.loot["jsFiles"].items():
                print(f"    \n{SourceUrl.strip()} :")
                for JsFile in JsFiles:
                    print(f"       - {JsFile.strip()}")
        else:
            print("  No JavaScript files found.")
        print("\n" + "=" * 60)

        # Display Directories
        print("\nDirectories Discovered:")
        if self.loot["directories"]:
            for SourceUrl, directories in self.loot["directories"].items():
                print(f"    \n{SourceUrl.strip()} :")
                if directories:
                    for directory in directories:
                        print(f"       - {directory.strip()}")
        else:
            print("  No directories found.")
        print("\n" + "=" * 60)

        # Display HTML Comments
        print("\nHTML Comments Found:")
        if self.loot["comments"]:
            for SourceUrl, comments in self.loot["comments"].items():
                print(f"    \n{SourceUrl.strip()} :")
                for comment in comments:
                    print(f"       {comment.strip()}")
        else:
            print("  No HTML comments found.")
        print("\n" + "=" * 60)

    #save output to a file
    def SaveOutputToFile(self,filename,url,depth=1):
        OutputFile = open(filename,'w')

        print("="*60 +"\n",file=OutputFile)
        print(f"Target URL  : {url}\nDepth Level : {depth}\n",file=OutputFile)
        print("\n"+ "="*60 + "\n",file=OutputFile)

        print("\n\n\n"+ "=" * 60,file=OutputFile)
        print("     Data Collection Summary ",file=OutputFile)
        print("=" * 60 +"\n",file=OutputFile)

        # Subdomains
        print("Subdomains Found:",file=OutputFile)
        if self.loot["subdomains"]:
            for subdomain in self.loot["subdomains"]:
                print(f"  - {subdomain.strip()}",file=OutputFile)
        else:
            print("  No subdomains found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        # Email addresses
        print("\nEmail addresses Found:",file=OutputFile)
        if self.loot["emails"]:
            for email in self.loot["emails"]:
                print(f"  - {email.strip()}",file=OutputFile)
        else:
            print("  No email addresses found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        # Links
        print("\nLinks Found:",file=OutputFile)
        if self.loot["links"]:
            for link in self.loot["links"]:
                print(f"   - {link.strip()}",file=OutputFile)
        else:
            print("  No links found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        # JavaScript Files
        print("\nJavaScript Files Discovered:",file=OutputFile)
        if self.loot["jsFiles"]:
            for SourceUrl, JsFiles in self.loot["jsFiles"].items():
                print(f"    \n{SourceUrl.strip()} :",file=OutputFile)
                for JsFile in JsFiles:
                    print(f"       - {JsFile.strip()}",file=OutputFile)
        else:
            print("  No JavaScript files found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        # Directories
        print("\nDirectories Discovered:",file=OutputFile)
        if self.loot["directories"]:
            for SourceUrl, directories in self.loot["directories"].items():
                print(f"    \n{SourceUrl.strip()} :",file=OutputFile)
                if directories:
                    for directory in directories:
                        print(f"       - {directory.strip()}",file=OutputFile)
        else:
            print("  No directories found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        # HTML Comments
        print("\nHTML Comments Found:",file=OutputFile)
        if self.loot["comments"]:
            for SourceUrl, comments in self.loot["comments"].items():
                print(f"    \n{SourceUrl.strip()} :",file=OutputFile)
                for comment in comments:
                    print(f"       {comment.strip()}",file=OutputFile)
        else:
            print("  No HTML comments found.",file=OutputFile)
        print("\n" + "=" * 60,file=OutputFile)

        OutputFile.close()








class Main():

    def DisplayHelpMenu(self) -> None:
        print("""Usage:
    webloot.py <URL> [DEPTH] [OPTIONS]

Options:
    -h			Display this help menu.
    -o <FILENAME>	Save output to a file.
Arguments:
    URL			The target URL to scan (required)
    DEPTH     		Depth level for crawling sub-links (optional, default: 1)

Examples:
    webloot.py https://example.com
    webloot.py https://example.com 2
    webloot.py https://example.com -o output.txt
    webloot.py https://example.com 2 -o output.txt

Notes:
    - If DEPTH is not specified, the default level of 1 will be used.
    - Increasing DEPTH allows for a deeper crawl, which may extend execution time.
        """)

    def DisplayWeblootBanner(self) -> None:
        print("""
		       _     _             _   
		      | |   | |           | |  
	 __      _____| |__ | | ___   ___ | |_ 
	 \ \ /\ / / _ \ '_ \| |/ _ \ / _ \| __|
	  \ V  V /  __/ |_) | | (_) | (_) | |_ 
	   \_/\_/ \___|_.__/|_|\___/ \___/ \__|
		                              
	   [author : o-sec]



""")

    def main(self) -> None:

        args = len(sys.argv)

        if args == 1:
            self.DisplayHelpMenu()
            exit()

        elif args == 2 and sys.argv[1].lower() == "-h":
            self.DisplayHelpMenu()
            exit()

        self.DisplayWeblootBanner()
        if args == 2:
            TargetUrl = sys.argv[1]
            self.webloot = Webloot(TargetUrl)
            self.webloot.CollectLoot(TargetUrl)
            self.webloot.DisplayCollectedLoot()

        elif args == 3:
            TargetUrl = sys.argv[1]
            depth = int(sys.argv[2])
            self.webloot = Webloot(TargetUrl)
            self.webloot.CollectLoot(TargetUrl,depth)
            self.webloot.DisplayCollectedLoot()

        elif args == 4:
            TargetUrl = sys.argv[1]
            filename = sys.argv[3]
            self.webloot = Webloot(TargetUrl)
            self.webloot.CollectLoot(TargetUrl)
            self.webloot.DisplayCollectedLoot()
            self.webloot.SaveOutputToFile(filename,TargetUrl)

        elif args == 5:
            TargetUrl = sys.argv[1]
            depth = int(sys.argv[2])
            filename = sys.argv[4]
            self.webloot = Webloot(TargetUrl)
            self.webloot.CollectLoot(TargetUrl,depth)
            self.webloot.DisplayCollectedLoot()
            self.webloot.SaveOutputToFile(filename,TargetUrl,depth)


if __name__ ==  "__main__":
    main = Main()
    main.main()




