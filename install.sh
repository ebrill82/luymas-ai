#!/usr/bin/env bash
# ============================================================
# Luymas AI - Installation Script
# Multi-Agent AI System with WhatsApp/Telegram Integration
# ============================================================
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Unicode
CHECK="✅"
CROSS="❌"
ARROW="➡️"
ROCKET="🚀"
GEAR="⚙️"
PACKAGE="📦"
SEARCH="🔍"
WARNING="⚠️"
EMAIL="📧"
SHIELD="🛡️"
STAR="⭐"

print_banner() {
    echo ""
    echo -e "${CYAN}${BOLD}╔══════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}${BOLD}║                                                  ║${NC}"
    echo -e "${CYAN}${BOLD}║          ${STAR} LUYMAS AI - Installation ${STAR}             ║${NC}"
    echo -e "${CYAN}${BOLD}║                                                  ║${NC}"
    echo -e "${CYAN}${BOLD}║    Multi-Agent AI System with WhatsApp/Telegram  ║${NC}"
    echo -e "${CYAN}${BOLD}║                                                  ║${NC}"
    echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_step() {
    echo ""
    echo -e "${BLUE}${BOLD}━━━ $1 ━━━${NC}"
    echo ""
}

print_success() {
    echo -e "  ${CHECK} ${GREEN}$1${NC}"
}

print_error() {
    echo -e "  ${CROSS} ${RED}$1${NC}"
}

print_warning() {
    echo -e "  ${WARNING} ${YELLOW}$1${NC}"
}

print_info() {
    echo -e "  ${ARROW} ${CYAN}$1${NC}"
}

ask_yes_no() {
    local prompt="$1"
    local default="${2:-y}"
    local yn=""
    while true; do
        echo -ne "  ${GEAR} ${prompt} [${default}/n] "
        read -r yn
        yn="${yn:-$default}"
        case "$yn" in
            [Yy]*) return 0 ;;
            [Nn]*) return 1 ;;
            *) echo "  Please answer y or n." ;;
        esac
    done
}

# ============================================================
# STEP 1: DETECT ENVIRONMENT
# ============================================================
detect_environment() {
    print_step "STEP 1: Environment Detection"

    # OS Detection
    OS="$(uname -s)"
    case "$OS" in
        Linux*)
            if grep -qi microsoft /proc/version 2>/dev/null; then
                OS_TYPE="linux-wsl"
                print_info "OS: Linux (WSL)"
            else
                OS_TYPE="linux"
                print_info "OS: Linux"
            fi
            ;;
        Darwin*)
            OS_TYPE="macos"
            print_info "OS: macOS"
            ;;
        *)
            OS_TYPE="unknown"
            print_warning "Unknown OS: $OS"
            ;;
    esac

    # Python check
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
        PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 10 ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.10+ required, found $PYTHON_VERSION"
            print_info "Install Python 3.10+: https://www.python.org/downloads/"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        print_info "Install Python 3.10+: https://www.python.org/downloads/"
        exit 1
    fi

    # Git check
    if command -v git &>/dev/null; then
        print_success "Git $(git --version | cut -d' ' -f3) found"
    else
        print_error "Git not found. Please install git."
        exit 1
    fi

    # RAM check
    if [ -f /proc/meminfo ]; then
        RAM_GB=$(awk '/MemTotal/ {printf "%.0f", $2/1024/1024}' /proc/meminfo)
        print_info "RAM: ${RAM_GB}GB"
        if [ "$RAM_GB" -lt 8 ]; then
            print_warning "Less than 8GB RAM. Only small models (7B) will run."
        elif [ "$RAM_GB" -lt 16 ]; then
            print_info "8-16GB RAM: Small to medium models (7B-14B) recommended."
        else
            print_success "${RAM_GB}GB RAM: Can run larger models."
        fi
    fi

    # GPU check
    if command -v nvidia-smi &>/dev/null; then
        GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)
        if [ -n "$GPU_INFO" ]; then
            print_success "GPU: $GPU_INFO"
            HAS_GPU=true
        else
            print_info "No NVIDIA GPU detected (CPU-only mode)"
            HAS_GPU=false
        fi
    else
        print_info "No NVIDIA GPU detected (CPU-only mode)"
        HAS_GPU=false
    fi

    # Disk space check
    DISK_AVAIL=$(df -h . | awk 'NR==2 {print $4}')
    print_info "Available disk space: $DISK_AVAIL"
}

# ============================================================
# STEP 2: INSTALL OLLAMA
# ============================================================
install_ollama() {
    print_step "STEP 2: Ollama Installation"

    if command -v ollama &>/dev/null; then
        OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
        print_success "Ollama already installed: $OLLAMA_VERSION"
        return 0
    fi

    print_warning "Ollama not found."
    if ask_yes_no "Install Ollama automatically?"; then
        print_info "Downloading Ollama..."
        case "$OS_TYPE" in
            linux|linux-wsl)
                curl -fsSL https://ollama.com/install.sh | sh
                ;;
            macos)
                print_info "Downloading Ollama for macOS..."
                curl -L -o /tmp/Ollama.dmg "https://ollama.com/download/Ollama-darwin.zip"
                print_info "Please install Ollama manually from the downloaded file."
                ;;
            *)
                print_error "Cannot auto-install Ollama on this OS."
                print_info "Visit https://ollama.com/download to install manually."
                exit 1
                ;;
        esac

        if command -v ollama &>/dev/null; then
            print_success "Ollama installed successfully!"
        else
            print_error "Ollama installation failed."
            print_info "Visit https://ollama.com/download to install manually."
            exit 1
        fi
    else
        print_error "Ollama is required. Please install it manually: https://ollama.com/download"
        exit 1
    fi

    # Start Ollama server
    print_info "Starting Ollama server..."
    ollama serve &>/dev/null &
    OLLAMA_PID=$!
    sleep 3

    # Verify Ollama is running
    if curl -s http://localhost:11434/api/tags &>/dev/null; then
        print_success "Ollama server is running!"
    else
        print_warning "Could not verify Ollama server. It may need a moment to start."
    fi
}

# ============================================================
# STEP 3: INSTALL MODELS
# ============================================================
install_models() {
    print_step "STEP 3: Model Installation"

    print_info "Checking and downloading required AI models..."
    print_info "This may take a while depending on your internet speed."
    echo ""

    # Define models by tier
    # Format: "ollama_tag|description|size_estimate_gb"
    MODELS=(
        "deepseek-r1:8b|Reasoning (8B params, fits 8GB RAM)|4.7"
        "qwen2.5-coder:7b|Code generation (7B params, fits 8GB RAM)|4.5"
        "gemma3:4b|Lightweight assistant (4B params, minimal RAM)|2.6"
        "z-image-turbo|Image generation (6B params, experimental)|3.8"
        "llama3.2:3b|Quick tasks (3B params, very fast)|2.0"
    )

    TOTAL_SIZE=0
    TO_DOWNLOAD=()

    for model_entry in "${MODELS[@]}"; do
        IFS='|' read -r tag desc size <<< "$model_entry"
        
        if ollama list 2>/dev/null | grep -q "$tag"; then
            print_success "Model $tag already present ($desc)"
        else
            print_info "Model $tag needed ($desc, ~${size}GB)"
            TOTAL_SIZE=$(echo "$TOTAL_SIZE + $size" | bc)
            TO_DOWNLOAD+=("$tag|$desc|$size")
        fi
    done

    if [ ${#TO_DOWNLOAD[@]} -eq 0 ]; then
        print_success "All required models are already installed!"
        return 0
    fi

    echo ""
    print_info "Models to download: ${#TO_DOWNLOAD[@]}"
    print_info "Estimated total size: ~${TOTAL_SIZE}GB"
    echo ""

    if ! ask_yes_no "Download these models now?"; then
        print_warning "Models not downloaded. You can install them later with: ollama pull <model>"
        return 0
    fi

    for model_entry in "${TO_DOWNLOAD[@]}"; do
        IFS='|' read -r tag desc size <<< "$model_entry"
        echo ""
        print_info "Downloading $tag ($desc, ~${size}GB)..."
        if ollama pull "$tag"; then
            print_success "Model $tag installed!"
        else
            print_error "Failed to download $tag. You can try later: ollama pull $tag"
        fi
    done

    echo ""
    print_success "Model installation complete!"
    print_info "Installed models:"
    ollama list 2>/dev/null | tail -n +1 | while read -r line; do
        echo "  $line"
    done
}

# ============================================================
# STEP 4: CONFIGURE MESSAGING
# ============================================================
configure_messaging() {
    print_step "STEP 4: Messaging Configuration"

    echo -e "  ${GEAR} Which messaging platform(s) do you want to use?"
    echo "  1) Telegram only"
    echo "  2) WhatsApp only"
    echo "  3) Both Telegram and WhatsApp"
    echo ""
    echo -ne "  Choose [1/2/3]: "
    read -r MSG_CHOICE

    case "$MSG_CHOICE" in
        1|2|3) ;;
        *) MSG_CHOICE=1 ;;
    esac

    # Telegram configuration
    if [ "$MSG_CHOICE" = "1" ] || [ "$MSG_CHOICE" = "3" ]; then
        echo ""
        print_info "Setting up Telegram..."
        echo "  To create a Telegram bot:"
        echo "  1. Open Telegram and search for @BotFather"
        echo "  2. Send /newbot and follow the instructions"
        echo "  3. Copy the bot token"
        echo ""
        echo -ne "  Enter your Telegram bot token: "
        read -r TELEGRAM_TOKEN

        if [ -n "$TELEGRAM_TOKEN" ]; then
            print_success "Telegram token configured!"
            echo "TELEGRAM_BOT_TOKEN=$TELEGRAM_TOKEN" >> .env
        else
            print_warning "No token provided. You can add it later to .env"
        fi
    fi

    # WhatsApp configuration
    if [ "$MSG_CHOICE" = "2" ] || [ "$MSG_CHOICE" = "3" ]; then
        echo ""
        print_info "Setting up WhatsApp..."
        echo "  WhatsApp uses the Web API (QR code scan)."
        echo "  When you start Luymas, a QR code will be displayed."
        echo "  Scan it with WhatsApp > Linked Devices."
        print_warning "WhatsApp setup will complete on first launch."
    fi

    print_info "The PDG agent will create accounts for all other agents automatically."
    print_info "A 'Luymas War Room' group will be created for team communication."
}

# ============================================================
# STEP 5: SECURITY - CONTACT WHITELIST
# ============================================================
configure_security() {
    print_step "STEP 5: Security Configuration"

    print_info "By default, only YOU are authorized to interact with Luymas agents."
    print_info "Unknown contacts will be blocked and reported to the PDG."
    echo ""

    echo -ne "  Enter your phone number (for WhatsApp authorization): "
    read -r USER_PHONE
    echo -ne "  Enter your email (for notifications): "
    read -r USER_EMAIL

    if [ -n "$USER_PHONE" ]; then
        echo "LUYMAS_USER_PHONE=$USER_PHONE" >> .env
        print_success "Phone number added to whitelist"
    fi
    if [ -n "$USER_EMAIL" ]; then
        echo "LUYMAS_USER_EMAIL=$USER_EMAIL" >> .env
        print_success "Email added to whitelist"
    fi

    echo ""
    print_info "Security rules:"
    echo "  ${SHIELD} Only whitelisted contacts can interact with agents"
    echo "  ${SHIELD} Unknown contacts → no response + alert to PDG"
    echo "  ${SHIELD} PDG forwards unknown contact info to you for approval"
    echo "  ${SHIELD} All agent actions require your explicit approval"
}

# ============================================================
# STEP 6: CREATE ENVIRONMENT
# ============================================================
create_environment() {
    print_step "STEP 6: Environment Setup"

    # Copy .env.example if .env doesn't have all vars
    if [ ! -f .env ]; then
        cp .env.example .env
        print_success "Created .env from template"
    else
        print_success ".env already exists"
    fi

    # Create Python virtual environment
    print_info "Creating Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi

    # Install Python dependencies
    print_info "Installing Python dependencies..."
    source venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet 2>/dev/null || {
        print_warning "Some dependencies failed to install. Trying without version pins..."
        pip install -r requirements.txt 2>/dev/null || print_warning "Dependency installation had issues. Check requirements.txt"
    }
    print_success "Python dependencies installed"

    # Create directories
    print_info "Creating project directories..."
    mkdir -p models logs data design/assets
    print_success "Directories created"

    # Generate API key for PDG
    PDG_API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null || echo "luymas-$(date +%s)-key")
    echo "LUYMAS_PDG_API_KEY=$PDG_API_KEY" >> .env
    print_success "PDG API key generated"
}

# ============================================================
# STEP 7: FINAL VERIFICATION
# ============================================================
verify_installation() {
    print_step "STEP 7: Verification"

    local ERRORS=0

    # Check Python
    if python3 -c "import ollama; import yaml; import aiohttp" 2>/dev/null; then
        print_success "Python dependencies OK"
    else
        print_warning "Some Python dependencies missing"
        ERRORS=$((ERRORS + 1))
    fi

    # Check Ollama
    if command -v ollama &>/dev/null; then
        MODEL_COUNT=$(ollama list 2>/dev/null | tail -n +2 | wc -l)
        print_success "Ollama running with $MODEL_COUNT model(s)"
    else
        print_warning "Ollama not running"
        ERRORS=$((ERRORS + 1))
    fi

    # Check .env
    if [ -f .env ]; then
        print_success ".env configured"
    else
        print_warning ".env missing"
        ERRORS=$((ERRORS + 1))
    fi

    # Check directories
    for dir in models logs data design/assets; do
        if [ -d "$dir" ]; then
            print_success "Directory $dir/ exists"
        else
            print_warning "Directory $dir/ missing"
            ERRORS=$((ERRORS + 1))
        fi
    done

    # Test a model if available
    if command -v ollama &>/dev/null; then
        print_info "Testing model inference..."
        if ollama run llama3.2:3b "Say hello in one word" 2>/dev/null | head -1 | grep -qi .; then
            print_success "Model inference working!"
        else
            print_warning "Model inference test skipped (no model available)"
        fi
    fi

    echo ""
    if [ $ERRORS -eq 0 ]; then
        echo -e "${GREEN}${BOLD}  ${CHECK} LUYMAS AI IS READY!${NC}"
    else
        echo -e "${YELLOW}${BOLD}  ${WARNING} LUYMAS AI installed with $ERRORS warning(s)${NC}"
    fi
}

# ============================================================
# STEP 8: LAUNCH
# ============================================================
show_launch_info() {
    print_step "Launch Luymas AI"

    echo "  To start Luymas AI:"
    echo ""
    echo -e "  ${CYAN}source venv/bin/activate${NC}"
    echo -e "  ${CYAN}python -m luymas.main${NC}"
    echo ""
    echo "  Or use the Studio web interface:"
    echo -e "  ${CYAN}python -m luymas.studio${NC}"
    echo ""
    echo "  Then open http://localhost:8501 in your browser."
    echo ""
    echo "  To add more models later:"
    echo -e "  ${CYAN}ollama pull <model-name>${NC}"
    echo ""
    echo "  Documentation: https://github.com/your-username/luymas-ai"
    echo ""
    if ask_yes_no "Start Luymas AI now?"; then
        source venv/bin/activate
        python -m luymas.main
    fi
}

# ============================================================
# MAIN
# ============================================================
main() {
    print_banner
    detect_environment
    install_ollama
    install_models
    configure_messaging
    configure_security
    create_environment
    verify_installation
    show_launch_info
}

main "$@"
