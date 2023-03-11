#!/bin/sh

VERSION=$(cat share/torbrowser-launcher/version)

build_rpm(){

# clean up from last build
rm -r build dist

# build binary package
python3 setup.py bdist_rpm --requires="python3-qt5, python3-gpg, python3-requests, python3-pysocks, python3-packaging, gnupg2"

}

# safety for beginners, blackPanther OS users
if [ -f "/etc/blackPanther-release" ];then

        case "$LANG" in
        hu*)
        no_text='\tMegszakítva!\n\n Amennyiben telepíteni akarod a hivatalos csaomagot, használd az alábbi műveletet:\n\n\ttelepites tor-browser-launcher'
        echo ''
        echo '  Egyéni TOR csomag létrehozása ...'
        echo '  A TOR hivatalos csomag elérhető a rendszer tárolójában is, elképzelhető, hogy az általad létrehozott csomag'
        echo '  helytelen függőségeket tartalmazhat, vagy működési hibát okozhat.'
        accept="        Ennek ellenére biztosan létrehozod a saját csomagod? i=igen n=nem (i/n)"
        ;;
        *)
        no_text='\tCancelled!\n\n If you want to install the official package, use the following procedure:\n\n\tinstalling tor-browser-launcher'
        echo ''
        echo '  Creating a custom TOR package...'
        echo '  The official TOR package is also available in the system repository,'
        echo '  it is possible that it is the package you created it may contain '
        echo '  incorrect dependencies or cause a malfunction.'
        accept="        Still, are you sure you'll create your own package? y=yes n=no (y/n)"
        ;;
        esac

    echo ""
    ANSWER=""
    while [ -z "${ANSWER}" ] ; do
      echo -en "$accept : "
      read ANSWER
      UCANSWER=`echo "${ANSWER}" | tr '[a-z]' '[A-Z]'`
      case "${UCANSWER}" in
      "I"|"YES"|"Y")
        ;;
      "NO"|"N")
        echo ""
        echo -e "$no_text"
        echo ""
        exit 1
        ;;
      *)
        ANSWER=""
        ;;
      esac
    done
   
build_rpm

echo ""
    case $LANG in 
      hu*)
        if [ -f "dist/torbrowser-launcher-$VERSION-1.noarch.rpm" ];then
            echo "A telepítéshez használd:"
            echo "telepites dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
        else
            echo " Hiányzó csomag! Lehet, hogy a saját RPM létrehozása nem sikerült..."
        fi
      ;;
      *)
        if [ -f "dist/torbrowser-launcher-$VERSION-1.noarch.rpm" ];then
            echo " To install, run:"
            echo " installing dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
        else
            echo " Missing package! The own RPM creation may failed..."
        fi
      ;;
    esac
    echo ""
  exit 0
fi

build_rpm
echo ""
echo " To install, run:"
echo " sudo dnf install dist/torbrowser-launcher-$VERSION-1.noarch.rpm"
echo ""



