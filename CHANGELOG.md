# Changelog

## 2026-09-14

- Updated `pcsc-lite` from 2.3.0 to 2.5.1.
- Updated `pcsc-tools` from 1.7.3 to 1.7.5.
- Updated `acsccid` from 1.1.11 to 1.1.13.
- Updated `pyscard` from 2.2.0 to 2.3.1.
- Disabled unnecessary systemd integration in the snap's `pcsc-lite` build.
- Routed `pcsc-scan` through the Perl launcher so `ATR_analysis` can locate
  bundled Perl modules such as `Getopt::Std`.
- Removed redundant global plug declarations.

## 2026-09-12

- Updated `cryptnox-cli` from 1.0.3 to 1.0.4.
- Updated the CCID source to 1.8.3.
