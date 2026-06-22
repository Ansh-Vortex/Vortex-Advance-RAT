{ pkgs ? import <nixpkgs> {} }:
(pkgs.buildFHSEnv {
  name = "python-env";
  targetPkgs = pkgs: (with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
    python3Packages.tkinter
    stdenv.cc.cc
    binutils
    zlib
    glibc
    glibc.dev
    portaudio
    pkg-config
    tk
    tcl
  ]);
  runScript = pkgs.writeScript "run" ''
    #!${pkgs.bash}/bin/bash
    export LIBRARY_PATH=${pkgs.glibc}/lib:${pkgs.glibc.dev}/lib:${pkgs.stdenv.cc.cc.lib}/lib
    export C_INCLUDE_PATH=${pkgs.glibc.dev}/include
    export TCL_LIBRARY=${pkgs.tcl}/lib
    export TK_LIBRARY=${pkgs.tk}/lib
    export PYTHONPATH=${pkgs.python3Packages.tkinter}/${pkgs.python3.sitePackages}:$PYTHONPATH
    [ ! -d .venv ] && python3 -m venv --system-site-packages .venv
    source .venv/bin/activate
    exec bash
  '';
}).env
