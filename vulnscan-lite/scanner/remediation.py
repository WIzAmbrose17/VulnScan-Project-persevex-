TIPS = {
    "Content-Security-Policy": {
        "why": "No CSP header means the browser will run scripts from any source.",
        "nginx": 'add_header Content-Security-Policy "default-src \'self\'";',
        "apache": 'Header set Content-Security-Policy "default-src \'self\'"',
    },
    "X-Frame-Options": {
        "why": "Site can be embedded in a hidden iframe (clickjacking).",
        "nginx": 'add_header X-Frame-Options "SAMEORIGIN";',
        "apache": 'Header always set X-Frame-Options "SAMEORIGIN"',
    },
    "Strict-Transport-Security": {
        "why": "Browser may still try plain HTTP first.",
        "nginx": 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
        "apache": 'Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"',
    },
    "certificate_valid": {
        "why": "TLS certificate missing, expired or invalid.",
        "nginx": "Run certbot renew and reload nginx.",
        "apache": "Run certbot renew and restart apache.",
    },
    "certificate_expiring_soon": {
        "why": "Certificate expires in less than 30 days.",
        "nginx": "sudo systemctl enable certbot.timer",
        "apache": "sudo systemctl enable certbot.timer",
    },
    "weak_cipher_suite": {
        "why": "Server accepted an old/broken cipher.",
        "nginx": "ssl_ciphers HIGH:!aNULL:!MD5;\nssl_protocols TLSv1.2 TLSv1.3;",
        "apache": "SSLCipherSuite HIGH:!aNULL:!MD5\nSSLProtocol -all +TLSv1.2 +TLSv1.3",
    },
    "outdated_tls_version": {
        "why": "Server allowed an old TLS version.",
        "nginx": "ssl_protocols TLSv1.2 TLSv1.3;",
        "apache": "SSLProtocol -all +TLSv1.2 +TLSv1.3",
    },
    "https_available": {
        "why": "Could not connect over HTTPS at all.",
        "nginx": "sudo certbot --nginx -d yourdomain.com",
        "apache": "sudo certbot --apache -d yourdomain.com",
    },
    "cms_up_to_date": {
        "why": "CMS version looks old, may have known bugs/exploits.",
        "nginx": "Update through the CMS admin panel, not a server config change.",
        "apache": "Update through the CMS admin panel, not a server config change.",
    },
    "cms_version_hidden": {
        "why": "Exact CMS version is visible in the page, gives attackers a head start.",
        "nginx": "Remove the generator meta tag from your theme.",
        "apache": "Remove the generator meta tag from your theme.",
    },
}


def get_tip(check_name):
    return TIPS.get(check_name, {"why": "no tip written for this one yet", "nginx": "-", "apache": "-"})
