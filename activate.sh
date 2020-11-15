
# Just for testing

here="$(cd "$(dirname "${BASH_SOURCE[0]}")"; pwd)"

if [[ ! -f "$here/venv/bin/activate" ]]; then
    python3 -m venv "$here/venv" || exit 1
fi

source "$here/venv/bin/activate"

export ACME_DNS_PROXY_HOME="$here"
