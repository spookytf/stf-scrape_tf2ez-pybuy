export A_RESET='\033[0m'
export A_GREEN='\033[00;32m'
echo -ne "${A_GREEN}Installing requirements for tf2easy scraper.${A_RESET}\n"
pip install -r requirements.txt
