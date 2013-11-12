#!/bin/sh
PACKAGE=fk-redis-stats
PACKAGE_ROOT="./fk-redis-stats-pkg"
VERSION="1.0"
ARCH=all

echo "Creating temp packaging directory ${PACKAGE_ROOT} ..."
mkdir -p $PACKAGE_ROOT
mkdir -p $PACKAGE_ROOT/DEBIAN
mkdir -p $PACKAGE_ROOT/var/lib/$PACKAGE
mkdir -p $PACKAGE_ROOT/etc/$PACKAGE
mkdir -p $PACKAGE_ROOT/etc/init.d

echo "Copying debian files to ${PACKAGE_ROOT} ..."
cp pkg/deb/$PACKAGE-init $PACKAGE_ROOT/etc/init.d/$PACKAGE

echo "Updating version in control file ..."
sed -e "s/VERSION/${VERSION}/" -i $PACKAGE_ROOT/DEBIAN/control

echo "Copying source and daemon to ${PACKAGE_ROOT} ..."
cp redis_stats.py $PACKAGE_ROOT/var/lib/$PACKAGE/redis_stats.py
cp daemon.py $PACKAGE_ROOT/var/lib/$PACKAGE/daemon.py

echo "Building debian ..."
dpkg-deb -b $PACKAGE_ROOT

echo "Removing older debians ..."
rm pkg/*.deb

echo "Renaming debian ..."
mv $PACKAGE_ROOT.deb pkg/${PACKAGE}_${VERSION}_${ARCH}.deb

echo "Removing temp directory ${PACKAGE_ROOT} ..."
rm -r $PACKAGE_ROOT

echo "Done."