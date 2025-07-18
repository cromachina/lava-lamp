{ pkgs ? import <nixpkgs> { } }:
let
  pythonldlibpath = pkgs.lib.makeLibraryPath (with pkgs; [
    stdenv.cc.cc
    libGL
    glib
    zlib
  ]);
in
pkgs.mkShell {
  packages = with pkgs; [
    python313
    xorg.libX11
    linuxHeaders
  ];
  shellHook = ''
    export LD_LIBRARY_PATH=${pythonldlibpath}
    python -m venv venv
    source venv/bin/activate
    exec bash
  '';
}