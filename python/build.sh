#!/bin/sh
# Build python/libheat.{dylib,so}: the Lean-compiled scheme plus the Lean
# runtime, statically linked into one self-contained shared library.
set -e
cd "$(dirname "$0")/.."
lake build HeatFFI:static
P=$(lean --print-prefix)
case "$(uname)" in
  Darwin) EXT=dylib; CXX=-lc++ ;;
  *)      EXT=so;    CXX="-lstdc++ -lpthread -lm -ldl" ;;
esac
cc -O2 -shared -fPIC -o python/libheat.$EXT python/heat_shim.c \
  -I "$P/include" \
  .lake/build/lib/libheat_HeatFFI.a \
  "$P/lib/lean/libInit.a" "$P/lib/lean/libleanrt.a" \
  "$P/lib/libuv.a" "$P/lib/libgmp.a" $CXX
echo "built python/libheat.$EXT"
