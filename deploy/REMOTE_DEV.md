# Claude Code Remote Development with AWS

Connect Claude Code (web/mobile) to your AWS EC2 instance for remote development and bot management.

---

## Quick Setup

### Step 1: Configure SSH Key

You need your AWS SSH key accessible to run remote commands.

**Option A: Key in Environment (Recommended for Mobile)**

```bash
# Set your AWS connection details
export AWS_HOST="13.231.xxx.xxx"  # Your EC2 public IP
export AWS_USER="ubuntu"

# If you have the key content, create the key file:
mkdir -p ~/.ssh
cat > ~/.ssh/fractal-key.pem << 'EOF'
-----BEGIN RSA PRIVATE KEY-----
YOUR_PRIVATE_KEY_CONTENT_HERE
-----END RSA PRIVATE KEY-----
EOF
chmod 400 ~/.ssh/fractal-key.pem
```

**Option B: Create Config File**

```bash
# Copy template
cp deploy/aws-remote.env.example ~/.fractal-aws.env

# Edit with your values
nano ~/.fractal-aws.env
```

### Step 2: Test Connection

```bash
# Quick test
./deploy/aws-remote.sh test

# Should output: "Connected to ip-xxx-xxx... - [date]"
```

### Step 3: Start Using!

```bash
# Check bot status
./deploy/aws-remote.sh status

# View logs
./deploy/aws-remote.sh logs

# Deploy changes
./deploy/aws-remote.sh deploy
```

---

## Available Commands

| Command | Description |
|---------|-------------|
| `status` | Show bot trading status |
| `logs [n]` | Show last n log lines (default: 50) |
| `logs-follow` | Follow logs in real-time |
| `ps` | Show container status |
| `start` | Start the bot |
| `stop` | Stop the bot |
| `restart` | Restart the bot |
| `deploy` | Pull latest code and restart |
| `report` | Show performance report |
| `resources` | Show system resources |
| `exec "cmd"` | Execute any command |
| `ssh` | Interactive SSH session |

---

## Workflow: Edit Locally, Deploy to AWS

### 1. Make Changes in Claude Code

```bash
# Edit files locally (this Claude Code instance)
# Claude Code edits the code here
```

### 2. Commit & Push

```bash
git add -A
git commit -m "Your changes"
git push
```

### 3. Deploy to AWS

```bash
./deploy/aws-remote.sh deploy
```

This will:
- SSH to your AWS server
- Pull latest code
- Rebuild and restart the bot

---

## Alternative: Direct SSH Commands

If you prefer raw SSH commands:

```bash
# Set variables
AWS_HOST="your-ip"
AWS_KEY="~/.ssh/fractal-key.pem"

# Run commands
ssh -i $AWS_KEY ubuntu@$AWS_HOST "docker ps"
ssh -i $AWS_KEY ubuntu@$AWS_HOST "cd FractalTrader && docker compose -f docker-compose.aws.yml logs --tail=20"
```

---

## Workflow for Mobile (iPhone)

### Method 1: Claude Code Web + SSH Wrapper

1. Open Claude Code in Safari
2. Configure SSH key (paste into terminal)
3. Use `./deploy/aws-remote.sh` commands

### Method 2: Split Approach

1. **Claude Code**: Edit code, commit, push
2. **Termius App**: SSH to AWS, pull & restart

### Method 3: GitHub Actions (Automated)

Setup CI/CD so pushing to main auto-deploys to AWS. (See `deploy/github-actions-deploy.yml` if available)

---

## Troubleshooting

### Connection Refused

```bash
# Check if instance is running in AWS Console
# Verify Security Group allows SSH (port 22) from your IP
# Check public IP hasn't changed (elastic IP recommended)
```

### Permission Denied

```bash
# Check key permissions
chmod 400 ~/.ssh/fractal-key.pem

# Verify correct key
ssh -i ~/.ssh/fractal-key.pem -v ubuntu@YOUR_IP
```

### Timeout

```bash
# Check AWS Security Group inbound rules
# Ensure port 22 is open to your IP
# Try from different network (mobile data vs wifi)
```

### Key Not Found

```bash
# Create config with correct path
echo 'AWS_KEY_PATH=/correct/path/to/key.pem' >> ~/.fractal-aws.env
```

---

## Security Notes

1. **Never commit SSH keys** to git
2. **Use `.fractal-aws.env`** (gitignored) for credentials
3. **Restrict Security Group** to your IP only
4. **Rotate keys** periodically
5. **Consider AWS SSM** for keyless access (advanced)

---

## Pro Tips

### Alias for Quick Access

```bash
# Add to ~/.bashrc or run in session
alias aws-bot="./deploy/aws-remote.sh"

# Now use:
aws-bot status
aws-bot logs
aws-bot deploy
```

### Watch Logs While Coding

```bash
# In one terminal/tab
./deploy/aws-remote.sh logs-follow

# In another - make edits and deploy
```

### Quick Status Check

```bash
# One-liner status
./deploy/aws-remote.sh exec "docker ps && free -h | head -2"
```

---

## What Claude Code Can Do Remotely

With this setup, Claude Code can:

- View bot logs and status
- Deploy code changes
- Start/stop/restart the bot
- Check system resources
- Run diagnostic commands
- Edit configuration files
- Debug issues in real-time

All from your mobile browser!
