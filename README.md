
# webloot

webloot is a Python-based asset discovery tool designed for web penetration testing. It takes a target URL and performs a deep crawl to identify key web assets such as subdomains, internal & external links, directories, JavaScript files, Email addresses and HTML comments. The tool is useful for reconnaissance during web penetration tests and capture-the-flag (CTF) challenges.

## Features

- **Subdomain Discovery**: Identifies subdomains related to the target domain.
- **Link Extraction**: Finds internal and external links.
- **Directory Enumeration**: Detects directories within the site structure.
- **JavaScript File Collection**: Lists JavaScript files for potential code analysis.
- **HTML Comment Extraction**: Collects HTML comments, which may contain useful information.
- **Email Addresses Collection**: Collects all Email addresses, within the the source code ( internal and external ).

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/o-sec/webloot.git
    cd webloot
    chmod +x webloot.py
    ```



## Usage

```bash
 ./webloot.py <URL> [DEPTH] [OPTIONS]
```

- `<URL>`: The target URL (required).
- `[DEPTH]`: Depth of link traversal (optional; default is `1`).
- `[OPTIONS]`: `-o <FILENAME>` Save output to a file (optional).


### Example

```bash
 ./webloot.py https://example.com 2 -o output.txt
```

In this example, webloot will crawl `https://example.com` with a depth level of `2`, exploring sub-links within the specified depth and save the output to a file with the name `output.txt`.



## Output

The tool provides organized output, displaying:
- **Target URL** and **Depth Level**
- **Subdomains Found**
- **Email addresses Found** (both internal and external)
- **Links Found** (both internal and external)
- **Directories Discovered**
- **JavaScript Files Detected**
- **HTML Comments Found**

### Sample Output

```plaintext



  		       _     _             _   
		      | |   | |           | |  
	 __      _____| |__ | | ___   ___ | |_ 
	 \ \ /\ / / _ \ '_ \| |/ _ \ / _ \| __|
	  \ V  V /  __/ |_) | | (_) | (_) | |_ 
	   \_/\_/ \___|_.__/|_|\___/ \___/ \__|
		                              
	   [author : o-sec]


  
  
======================

Target URL: https://example.com
Depth Level: 2

======================

[*] Collecting data...

Depth 2 | Progress  100%


=================================
Data Collection Summary
=================================

Subdomains Found:
   - sub1.example.com
   - sub2.example.com


=================================

Email addresses Found:
   - support@example.com
   - user@yahoo.com
   
=================================
   
Links Found:
   - https://example.com/about
   - https://example.com/contact
   - https://external.net/pic.png
=================================

JavaScript files Discovered:

https://example.com/ :
   - https://cdn.com/main.js
   - /content/swipe.js
   
https:/www.example.com/home.php :
   - /home/jsfiles/touch.js
      
=================================

Directories Discovered:

https://example.com/home.php :
   - /wp-content/
   - /support/
https://m.example.com/ :
   - /mobile/
   - /data/work/
   
=================================

HTML Comments Found:

https://example.com/login.html :
    <!-- Todo : add reset password function. -->
    
https://www.example.com/ :
    <!-- user = "admin" , password = "password123" . -->
    
=================================      

```

