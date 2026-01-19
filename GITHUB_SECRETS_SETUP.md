# Setting Up GitHub Secrets for Backend Deployment

## Required Secrets

You need to configure these secrets in your GitHub repository to enable automatic deployment.

### Navigation
1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Secrets and variables** → **Actions** (left sidebar)
4. Click **New repository secret**

---

## 1. EC2_SSH_KEY

**What it is:** Private SSH key to access your EC2 server

### How to get it:

#### Option A: Generate new key on your local machine
```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/aegis-deploy

# Copy private key content
cat ~/.ssh/aegis-deploy
```

#### Option B: Use existing EC2 key
```bash
# If you have a .pem file
cat ~/Downloads/your-ec2-key.pem
```

### Add to EC2:
```bash
# SSH to your EC2
ssh -i your-key.pem ubuntu@35.180.117.85

# Add public key to authorized_keys
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### Add to GitHub:
- **Name:** `EC2_SSH_KEY`
- **Value:** Entire private key content (including `-----BEGIN` and `-----END` lines)

---

## 2. EC2_HOST

**What it is:** IP address or domain of your EC2 server

### Value:
```
35.180.117.85
```

Or if you have a domain:
```
api.aegis-ignis.com
```

### Add to GitHub:
- **Name:** `EC2_HOST`
- **Value:** `35.180.117.85`

---

## 3. EC2_USER

**What it is:** SSH username for your EC2 server

### Common values:
- Amazon Linux: `ec2-user`
- Ubuntu: `ubuntu`
- Debian: `admin`

### How to check:
```bash
# When you SSH normally, this is the user
ssh ubuntu@35.180.117.85  ← this part
```

### Add to GitHub:
- **Name:** `EC2_USER`
- **Value:** `ubuntu` (or your specific user)

---

## 4. DEPLOY_PATH

**What it is:** Full path to your application on EC2

### Find your path:
```bash
# SSH to EC2
ssh ubuntu@35.180.117.85

# Check where your app is
pwd
# Example: /home/ubuntu/Aegis-IgnisGit
# Or: /var/www/html/aegis-ignis
```

### Add to GitHub:
- **Name:** `DEPLOY_PATH`
- **Value:** `/var/www/html/aegis-ignis` (or your actual path)

---

## Testing the Setup

### Step 1: Add all secrets
Verify all 4 secrets are added in GitHub Settings → Secrets and variables → Actions

### Step 2: Test SSH connection locally
```bash
# Use the same credentials
ssh -i ~/.ssh/aegis-deploy ubuntu@35.180.117.85 "cd /var/www/html/aegis-ignis && pwd"
```

### Step 3: Make a test commit
```bash
# Make a small change in backend
cd backend-laravel
echo "# Test" >> README.md
git add README.md
git commit -m "Test deployment workflow"
git push origin main
```

### Step 4: Watch GitHub Actions
- Go to repository → Actions tab
- You should see "Backend PR Tests & Deploy" running
- Click on it to see live logs

---

## Troubleshooting

### Error: "Permission denied (publickey)"
- Check EC2_SSH_KEY is complete (including BEGIN/END lines)
- Verify public key is in `~/.ssh/authorized_keys` on EC2
- Check EC2_USER is correct

### Error: "Host key verification failed"
- Workflow includes `ssh-keyscan` to fix this automatically
- If persists, manually add to GitHub workflow

### Error: "No such file or directory"
- Check DEPLOY_PATH is correct
- SSH to EC2 and verify path exists

### Can't find the application on EC2?
```bash
# SSH to EC2
ssh ubuntu@35.180.117.85

# Search for the repo
find ~/ -name "Aegis-IgnisGit" 2>/dev/null
find /var/www -name "Aegis-IgnisGit" 2>/dev/null
```

---

## Security Best Practices

### ✅ DO:
- Use ed25519 keys (more secure than RSA)
- Keep private keys secret
- Use repository secrets (never commit keys)
- Rotate keys periodically

### ❌ DON'T:
- Share private keys
- Commit keys to repository
- Use the same key for multiple services
- Use weak passwords for SSH

---

## Quick Copy-Paste Template

```bash
# 1. Generate new SSH key
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/aegis-github-deploy

# 2. Copy public key to EC2
ssh-copy-id -i ~/.ssh/aegis-github-deploy.pub ubuntu@35.180.117.85

# 3. Get private key for GitHub secret
cat ~/.ssh/aegis-github-deploy

# 4. Test connection
ssh -i ~/.ssh/aegis-github-deploy ubuntu@35.180.117.85 "echo 'Connection successful!'"
```

Then add these to GitHub Secrets:
- EC2_SSH_KEY = (output from step 3)
- EC2_HOST = 35.180.117.85
- EC2_USER = ubuntu
- DEPLOY_PATH = /var/www/html/aegis-ignis

---

**Need Help?** Check GitHub Actions logs for detailed error messages.
