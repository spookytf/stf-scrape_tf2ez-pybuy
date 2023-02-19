export A_RESET='\033[0m'
export A_GREEN='\033[00;32m'
echo -ne "${A_GREEN}Writing requirements for tf2easy scraper.${A_RESET}\n"
python -m pipreqs.pipreqs .
