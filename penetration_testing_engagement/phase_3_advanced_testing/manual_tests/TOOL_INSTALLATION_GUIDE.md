# MANUAL TESTING TOOLS - INSTALLATION & SETUP GUIDE

## 🛠️ ESSENTIAL TOOLS FOR MANUAL TESTING

### **1. BROWSER-BASED TOOLS (Easiest - Start Here)**

#### **Firefox/Chrome Developer Tools** ✅ Already Installed
- **Access:** Press `F12` or `Ctrl+Shift+I`
- **Best For:** Header analysis, response inspection, network monitoring
- **Cost:** Free

#### **Burp Suite Community Edition** 🔥 Recommended
- **Download:** https://portswigger.net/burp/communitydownload
- **Installation:**
  ```bash
  # Windows: Download .exe and run installer
  # Add to PATH during installation
  ```
- **Setup:**
  1. Start Burp Suite
  2. Go to Proxy tab
  3. Set browser proxy to 127.0.0.1:8080
  4. Import Burp certificate to browser
- **Best For:** Request interception, modification, repeating attacks
- **Cost:** Free (Community), $399/year (Professional)

---

### **2. COMMAND LINE TOOLS (Intermediate)**

#### **curl** ✅ Already Available (Windows 10+)
- **Test Installation:**
  ```bash
  curl --version
  ```
- **Best For:** HTTP requests, header analysis, rapid testing
- **Cost:** Free

#### **Postman** 🎯 User Friendly
- **Download:** https://www.postman.com/downloads/
- **Installation:** Download and run installer
- **Best For:** API testing, request collections, automated testing
- **Cost:** Free (with account), $12/month (Pro)

#### **Insomnia** (Alternative to Postman)
- **Download:** https://insomnia.rest/download
- **Best For:** REST API testing, GraphQL testing
- **Cost:** Free

---

### **3. SPECIALIZED PENETRATION TESTING TOOLS**

#### **OWASP ZAP** ✅ Already Installed
- **Location:** `"C:\Program Files\ZAP\Zed Attack Proxy\zap.bat"`
- **Best For:** Comprehensive automated + manual testing
- **Cost:** Free

#### **Nmap** (Network Scanner)
- **Download:** https://nmap.org/download.html
- **Installation:**
  ```bash
  # Windows: Download installer from website
  # Add to PATH during installation
  ```
- **Test Installation:**
  ```bash
  nmap --version
  ```
- **Best For:** Port scanning, service detection
- **Cost:** Free

#### **Nikto** (Web Scanner)
- **Installation (requires Perl):**
  ```bash
  # Windows: Use Docker or WSL
  docker run --rm -it securecodethoughts/nikto -h http://your-target
  ```
- **Best For:** Web server scanning, common vulnerabilities
- **Cost:** Free

---

### **4. BROWSER EXTENSIONS**

#### **Wappalyzer** 🔍 Technology Detection
- **Install:** Chrome Web Store / Firefox Add-ons
- **Search:** "Wappalyzer"
- **Best For:** Technology stack identification
- **Cost:** Free

#### **Cookie-Editor**
- **Install:** Chrome Web Store / Firefox Add-ons
- **Best For:** Session manipulation, cookie analysis
- **Cost:** Free

#### **User-Agent Switcher**
- **Install:** Chrome Web Store / Firefox Add-ons  
- **Best For:** Testing different user agents
- **Cost:** Free

---

## 🚀 QUICK START SETUP (5 Minutes)

### **Minimum Setup for Manual Testing:**

1. **Open Firefox/Chrome** (Already installed)
2. **Install Wappalyzer Extension**
3. **Download Postman** (5-minute install)
4. **Test curl command:**
   ```bash
   curl -I http://127.0.0.1:8000/
   ```

**That's it! You can now do 80% of manual testing.**

---

### **Advanced Setup (30 Minutes):**

1. **Install Burp Suite Community:**
   - Download from PortSwigger
   - Configure browser proxy
   - Import certificate

2. **Install Nmap:**
   - Download Windows installer
   - Add to PATH

3. **Test Complete Setup:**
   ```bash
   # Test all tools
   curl --version
   nmap --version
   # Start Burp Suite
   # Open Postman
   ```

---

## 📚 TOOL COMPARISON

| Tool | Difficulty | Best Use Case | Cost |
|------|------------|---------------|------|
| **Browser DevTools** | Easy | Header analysis, basic inspection | Free |
| **curl** | Easy | Quick HTTP tests, scripting | Free |
| **Postman** | Easy | API testing, organized requests | Free |
| **Burp Suite Community** | Medium | Request interception, manual testing | Free |
| **OWASP ZAP** | Medium | Comprehensive scanning | Free |
| **Burp Suite Pro** | Hard | Professional pentesting | $399/yr |
| **Nmap** | Hard | Network reconnaissance | Free |

---

## 🎯 RECOMMENDED LEARNING PATH

### **Day 1: Browser Basics**
- Use Firefox DevTools
- Install Wappalyzer
- Test basic curl commands

### **Day 2: API Testing**
- Install and learn Postman
- Create test collections
- Practice request modification

### **Day 3: Proxy Testing**
- Install Burp Suite Community
- Configure browser proxy
- Practice request interception

### **Day 4: Advanced Tools**
- Try OWASP ZAP manual mode
- Install Nmap for port scanning
- Combine multiple tools

---

## 💡 PRO TIPS

1. **Start Simple:** Begin with browser DevTools and curl before moving to complex tools
2. **One Tool at a Time:** Master each tool before moving to the next
3. **Document Everything:** Save your commands and findings
4. **Practice on Your Own App:** Always test on your ConnectlyIPT application first
5. **Read the Docs:** Each tool has excellent documentation

---

## 🆘 TROUBLESHOOTING

### **Common Issues:**

#### **Burp Suite Certificate Issues:**
```bash
# Solution: Import Burp certificate to browser
# Go to http://burp when proxy is running
# Download cacert.der and import to browser
```

#### **curl Not Found:**
```bash
# Windows 10/11: curl should be pre-installed
# If missing, download from: https://curl.se/windows/
```

#### **Postman Login Required:**
```bash
# Create free account at https://www.postman.com/
# Required for saving collections
```

#### **Browser Proxy Issues:**
```bash
# Reset browser proxy settings to "No proxy"
# Restart browser after changing proxy settings
```

---

## ✅ VERIFICATION CHECKLIST

**Test each tool after installation:**

- [ ] Browser DevTools: Press F12, see Network tab
- [ ] curl: Run `curl --version`  
- [ ] Postman: Create new request, send to httpbin.org
- [ ] Burp Suite: Start proxy, intercept browser request
- [ ] Wappalyzer: Visit a website, see detected technologies

**Ready for Manual Testing!** 🚀

Now go back to the `MANUAL_PENETRATION_TESTING_GUIDE.md` and start with **Phase 1: Information Disclosure Testing**!