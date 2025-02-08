# HackSphere_CodeBreakers
A Email Spam Prevention tool, the basic idea is that the user whenever suspects an suspicious email, the user just forwards the potential spam email to our designated support email. The designated support email is linked with a python script that checks for any new email and then the processing starts. 
The Process:
1. Check the sender email of the forwarded email for SPF, DMARC and DKIM.
2. Check the body of the email for potential phishing and suspicious links.
3. Check the attachments of the forwarded email for potential malware and virus through virustotal api.

After processing the user would receive a return email within 2-3 mins with a detailed report of the process. 
Additional Feature:
1. A browser Extension that does the same process
2. A Web Interface, where upon receiving permission all the emails are checked, and a mark is assigned to each email which displays whether the email is safe or unsafe.
