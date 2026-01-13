#!/usr/bin/env python

# Should work on either python2 or python3

# gencert.py
#
# Copyright (c) 2020, Toshiba Global Commerce Solutions, Inc.
#
# By: Buzzy Brown
#
# Changes/Versions:
#    1.0 - Initial drop to Susan
#    1.1 - Remove "aaa" from CN; add -keep flag; fix bugs, improve help
#    1.2 - Use openssh for random data; improve help; mark SAN as critical if
#          more than one name listed (RFC5280). Add support for -iter flag when
#          it becomes available; Add cert nicknames (java alias); add --quiet
#          flag; clean up code a bit; add CA cert serial number
#    1.3 - Update help; add tips and examples
#    1.4 - Add --ouname, --store, and --term flags; update examples; allow
#          controller id to be a range.
#    1.5 - Allow CN to be set for each certificate (allowing wildcard FQDNs in
#          the CN; make default CN in client cert a hostname; use OU name in
#          default aliases; change --ouname flag to --ou_name; Remove SAN extension
#          from the CA cert; rename some of the temp files to make more sense
#    1.6 - Add --java flag and --keysize flags; reorganize code a lot to use
#          settings for command/help expansion. Change output files/flags referring
#          to "client" to "ca" (i.e. -client_cn to -ca_cn)
#    1.7 - Fix bug if ou_name not set

# Generates a new CA certificate and uses that to sign a new non-CA certificate.
#
# If we wanted to use a common CA for many certs, there are likely better ways
# to do it than the command line (especially since some versions of openSSL
# has some bugs.  In general, we'd want to:
#    * Use a unique serial # for each cert signed
#    * Keep track of previously created certs (in an index file)
#    * Perhaps allow for revocation (we'd have to make the CRL accessible and
#      likely add a record in the cert for where it's found). Would also need to
#      add cRLSign to the CA key usage.
#    * Right now the DN in both the CA and normal certificates match (so "issued by"
#      and "issued to" match). The CA should probably have a more descriptive name.

from __future__ import print_function
import os
import sys
import traceback
import argparse
import subprocess
import re

# For x509 stuff required by the browser, see:
#    https://developer.mozilla.org/en-US/docs/Mozilla/Security/x509_Certificates

# Various default settings

DEFAULT_CONTROLLER_LIST = [ "cc", "dd" ]

DEFAULT_PASSWORD = "PASSWORD"

DEFAULT_ORGANIZATION = "TGCS Software"

DEFAULT_KEYSIZE = 4096

# If we can use the iter flag with newer versions of OpenSSL, do so. Java uses
# 50000 iterations in the MAC hash...so let's pick that instead of the default 2048

DEFAULT_ITER_COUNT = 50000

# This is the template used to generate the certificate. We must generate both a CA
# certificate and a non-CA certificate signed by the CA. Although most programs would
# work fine with EITHER, Firefox has recently insisted we do things the "proper"
# way even for self signed certificates...specifically the browser will only
# trust "CA" certificates and web servers must present non-CA (client) certs.

CNF_TEMPLATE = \
"""
# See https://www.openssl.org/docs/manmaster/man1/openssl-req.html

# Default settings - Normally 2048 bit key with sha256; use higher length key and
# hash if possible. This produces an UNENCRYPTED key (as if the -nodes
# flag was used).
#
# For some reason I cannot change days here...use the command line flag

[ req ]
default_bits       = {KEYSIZE}
default_md         = sha256
default_keyfile    = key.pem
prompt             = no
encrypt_key        = no
days               = 365

# Name the section where we get the fields for the FQDN
distinguished_name = req_distinguished_name

# Include the extensions whether or not they use the -x509 flag
req_extensions     = x509_ext
x509_extensions    = x509_ext

# Used to generate the DN. Only the commonName/CN and maybe OU is required for a
# web certificate. The CN is used to identify the "main" web server id. The OU
# is listed in the description page in the CA list (after you import it) so it
# should be set to make it identifyable. The fields are typically 1-64 characters
#
# The organizationName is what appears in the browser certificate list. You can
# use multiple O fields if needed like the OU field below.

[ req_distinguished_name ]
# countryName            = "US"                              # C=
# stateOrProvinceName    = "NC"                              # ST=
# localityName           = "Durham"                          # L=
# postalCode             = "27703"                           # L/postalcode=
# streetAddress          = "3901 S. Miami Blvd"              # L/street=
organizationName         = "{ORGANIZATION}"                  # O=
organizationalUnitName   = "{OU_NAME}"                       # OU=
commonName               = "{COMMON_NAME}"                   # CN=
# emailAddress           = "support@toshibacommerce.com"     # CN/emailAddress=

{X509_EXT}
"""

# The extensions are separate because it's used in multiple places and we use
# different settings in the CA. Some usage fields (like for email) have been
# removed.
#
# This ALWAYS sets the subjectAltName field even (if there is only one host
# name) as Firefox now requires it, however it's only marked as critical if
# there is more than one name listed (otherwise the cert won't work as we expect
# if for some reason the client doesn't understand the extension).
#
# See http://www.openssl.org/docs/manmaster/man5/x509v3_config.html

X509_EXT_CA = \
"""
[ x509_ext ]
basicConstraints = critical,CA:TRUE
nsCertType = server
keyUsage = critical,digitalSignature,keyCertSign
extendedKeyUsage = serverAuth
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid, issuer
"""

# Regular certificate extensions

X509_EXT_CRT = \
"""
[ x509_ext ]
subjectAltName = {SAN_CRITICAL}@alternate_names             #@SAN
basicConstraints = CA:FALSE
nsCertType = server
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth

[ alternate_names ]                                         #@SAN
{ALT_NAMES}                                                 #@SAN
"""

# Global settings object from the argument parser. This is used BOTH to check
# validate settings AND in the expansion of various commands.

settings = None

# Run a command

def runCmd(cmd):
    if settings:
        if settings.verbose:
            print(">> %s" % cmd)
        cmd = cmd.format(**vars(settings))
        if settings.verbose:
            print("== %s\n" % cmd)

    sys.stdout.flush()
    sys.stderr.flush()

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE if settings.quiet else None, stderr=subprocess.STDOUT if settings.quiet else None, shell=True)

    output, _ = p.communicate()

    if p.returncode:
        if settings.quiet:
            sys.stdout.write(output)
        print("Error %d running: %s" % (p.returncode, cmd))

    return p.returncode

# Run a shell command, returning the exit code and output as a tuple

def getCmdOutput(cmd, wantStderr=False):
    if settings:
        if settings.verbose:
            print(">> %s" % cmd)
        cmd = cmd.format(**vars(settings))
        if settings.verbose:
            print("== %s\n" % cmd)

    sys.stdout.flush()
    sys.stderr.flush()

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT if wantStderr else None, shell=True)

    output, _ = p.communicate()

    if p.returncode and not wantStderr:
        print("Error %d running: %s" % (p.returncode, cmd))

    if sys.version_info.major > 2:
        output = output.decode("utf-8")

    return p.returncode, output

# Run a command with two different filenames and compare the output. The
# filename is indicated by the {FN} format string in the command.

def compareOutput(cmdTemplate, fn1, fn2):
    if settings.verbose:
        print("Comparing %s to %s" % (fn1, fn2))

    rc, out1 = getCmdOutput(cmdTemplate.replace("{FN}", fn1))

    if rc == 0:
        rc, out2 = getCmdOutput(cmdTemplate.replace("{FN}", fn2))

        if rc == 0 and out1 != out2:
            print("Output doesn't match for %s and %s" % (fn1, fn2))
            rc = -1

    return rc

# Generate a certificate using openssl

def genCertOpenSSL():
    global settings

    rc = 0

    # Set the initial set of default fields for configuration

    cnfFields = { "ORGANIZATION"  : settings.organization,
                  "OU_NAME"       : settings.ou_name,
                  "KEYSIZE"       : settings.keysize,
                  "COMMON_NAME"   : None,
                  "ALT_NAMES"     : "\n".join(settings.altNames),
                  "SAN_CRITICAL"  : "critical, " if settings.san_critical else "",
                  }

    # Filter out lines of each of the certificates above. Specifically,
    # if there is no need for a SAN field, don't include it.

    global X509_EXT_CRT
    global X509_EXT_CA

    if not cnfFields["ALT_NAMES"]:
        X509_EXT_CRT = "\n".join([line for line in X509_EXT_CRT.split("\n") if line.find("#@SAN") < 0])
        X509_EXT_CA  = "\n".join([line for line in X509_EXT_CA.split("\n")  if line.find("#@SAN") < 0])

    # CA creation file

    with open(settings.fn_tmp_ca_cnf, "w") as f:
        cnfFields["COMMON_NAME"] = settings.ca_cn
        cnfFields["X509_EXT"] = X509_EXT_CA.format(**cnfFields)
        f.write(CNF_TEMPLATE.format(**cnfFields))

    # Certificate creation file

    with open(settings.fn_tmp_server_cnf, "w") as f:
        cnfFields["COMMON_NAME"] = settings.server_cn
        cnfFields["X509_EXT"] = X509_EXT_CRT.format(**cnfFields)
        f.write(CNF_TEMPLATE.format(**cnfFields))

    # The ca and x509 signing commands make it REALLY hard to include the extensions
    # we want. Apparently this is partially due to a bug in the version of openssl
    # I'm using (https://unix.stackexchange.com/questions/371997/creating-a-local-ssl-certificate)
    #
    # Using the ca command is hard since it requires so much extra stuff it in the config
    # file and the x509 doesn't allow for a config file to be passed. I don't want to
    # all of the data from the default config file and don't want to risk it changing.
    # so I just create an extensions file specifically for the signing command.

    with open(settings.fn_tmp_server_ext, "w") as f:
        f.write(X509_EXT_CRT.format(**cnfFields))

    # Generate the CA certificate and the client p12 file containing it

    settings.x509IterFlag = "-iter %u" % settings.iterations if settings.iterations else ""

    # Create a serial number for the CA certificate

    rc, hexdata = getCmdOutput("openssl rand -hex 20")

    if rc == 0:
        settings.serial = "0x" + hexdata.strip()
        rc = runCmd("openssl req -new -x509 -out '{fn_ca_crt}' -keyout '{fn_tmp_ca_key}' -days '{age}' -set_serial '{serial}' -config '{fn_tmp_ca_cnf}' -passout 'pass:{password}'")

    if rc == 0:
        rc = runCmd("openssl pkcs12 -export -in '{fn_ca_crt}' -out '{fn_ca_p12}' -clcerts -nokeys -passout pass: -name '{ca_alias}' {x509IterFlag}")

    # Generate the certificate request

    if rc == 0:
        rc = runCmd("openssl req -new -out '{fn_tmp_server_csr}' -keyout '{fn_tmp_server_key}' -config '{fn_tmp_server_cnf}' -passout 'pass:{password}'")

    # Sign the CSR

    if rc == 0:
        # Create a serial number (browsers loose their minds if they see one reused and there
        # may be an attack that makes use of predicted values). It's a 20 byte hex string.

        rc, hexdata = getCmdOutput("openssl rand -hex 20")

        if rc == 0:
            settings.serial = "0x" + hexdata.strip()
            rc = runCmd("openssl x509 -req -in '{fn_tmp_server_csr}' -out '{fn_tmp_server_crt}' -CA '{fn_ca_crt}' -CAkey '{fn_tmp_ca_key}' -days '{age}' -set_serial '{serial}' -extfile '{fn_tmp_server_ext}' -extensions x509_ext")

    # Create a server PKCS file. You could ship/use the raw certificate or key files,
    # but using a the PKCS12 container provides a little more validation and is
    # a more standard format in many cases.

    if rc == 0:
        if not settings.quiet:
            print("Creating PKCS12 files")

        rc = runCmd("openssl pkcs12 -export -in '{fn_tmp_server_crt}' -out '{fn_server_p12}' -inkey '{fn_tmp_server_key}' -passout 'pass:{password}' -name '{server_alias}' {x509IterFlag}")

    # Initial help text

    helpLines = ["""
The following files were created

   {fn_server_p12} - This is your server certificate; it is password protected with
                the password '{password}' by default or the one provided on the
                command line otherwise. This file CONTAINS THE PRIVATE KEY of
                the certificate, so protect the password.

   {fn_server_crt} - The server certificate in PEM format. Some programs like nginx
                require the key in this format.

   {fn_server_key} - The server key in PEM format. THIS MUST BE PROTECTED, it is not
                password protected like it would be in a P12 file.

   {fn_ca_crt} - This is the client certificate in PEM format. It's a CA
                certificate (specifically the one used to sign the server
                certificate). The file is in PEM format, which allows it to be
                imported directly by many browsers.

   {fn_ca_p12} - Same as {fn_ca_crt} but in PKCS12 format, which allows it to be
                used as a java truststore. It has an empty password.
"""]

    # Export the key and certificate files from the P12 files so we can make sure they match.

    if rc == 0:
        if not settings.quiet:
            print("Exporting key/cert from P12 files")

        cmd = "openssl pkcs12 -in '{fn_server_p12}' -out '{fn_server_crt}' -nokeys -passin 'pass:{password}'"
        helpLines.append("To extract the server certificate:")
        helpLines.append("   "+cmd)
        helpLines.append("")
        rc |= runCmd(cmd)

        cmd = "openssl pkcs12 -in '{fn_server_p12}' -out '{fn_server_key}' -nocerts -nodes -passin 'pass:{password}'"
        helpLines.append("To extract the (unencrypted) server key:")
        helpLines.append("   "+cmd)
        helpLines.append("")
        rc |= runCmd(cmd)

        if 0 == rc:
            if not settings.quiet:
                print("Verifying files")
            rc |= compareOutput("openssl x509 -in '{FN}' -noout -text", "{fn_tmp_server_crt}", "{fn_server_crt}")
            rc |= compareOutput("openssl rsa  -in '{FN}' -noout -text", "{fn_tmp_server_key}", "{fn_server_key}")

    return rc, helpLines

# Generate a certificate using Java
#
# SIGH - I **really** don't know if this is right or not. There are a lot of different
#        examples on the internet about how to create self-signed certificates

def genCertJava():
    global settings

    rc = 0

    # Remove existing files so keytool does not pitch a fit

    for fn in [ settings.fn_keystore, settings.fn_truststore, settings.fn_tmp_catrust ]:
        if os.path.exists(fn):
            os.remove(fn)
            if settings.verbose:
                print("Removed: %s" % fn)

    # Create the DN (distinguished name) fields.

    settings.ca_dn     = "o={organization}, ou={ou_name}, cn={ca_cn}".format(**vars(settings))
    settings.server_dn = "o={organization}, ou={ou_name}, cn={server_cn}".format(**vars(settings))

    # Generate the list of subject alternative names flags and any other extensions we need

    settings.extflags = "-ext san="
    extValues = []
    for name in settings.altNames:
        # Names come in in the format:
        #   DNS.1 = XXX
        #   DNS.2 = YYY
        #   IP.1  = x.x.x.x
        field  = name.split("=", 2)
        stype  = field[0].split(".")[0]
        svalue = field[1].strip()
        extValues.append(stype+":"+svalue)
    settings.extflags = "-ext 'san%s=%s'" % (":critical" if settings.san_critical else "", ",".join(extValues))

    # If there is no truststore password, fail

    if not settings.password_ts:
        print("The truststore password is required; use the --password_ts flag to set it.");
        rc = 1

    # TBD Allow choice of keyalg/sigalg? Allow JKS format?

    # Generate a temporary certificate for our self signing. Since we only use
    # it to sign one server certificate, we don't keep it around.

    if rc == 0:
        rc = runCmd("keytool -genkeypair -storetype PKCS12 -keystore '{fn_tmp_catrust}' -storepass '{password}' -keypass '{password}' -alias '{ca_alias}' -dname '{ca_dn}' -validity '{age}' -keyalg RSA -keysize '{keysize}' -ext BasicConstraints:critical,ca:true -ext KeyUsage:critical=digitalSignature,keyCertSign -ext ExtendedKeyUsage=serverAuth")

    # Export the certificate (only)

    if rc == 0:
        rc = runCmd("keytool -exportcert -keystore '{fn_tmp_catrust}' -storepass '{password}' -alias '{ca_alias}' -rfc -file '{fn_truststore_pem}'")

    # Go ahead and create the trust store since it contains only the CA certificate

    if rc == 0:
        rc = runCmd("keytool -importcert -keystore '{fn_truststore}' -storepass '{password_ts}' -file '{fn_truststore_pem}' -noprompt -alias '{ca_alias}'")

    # Generate a certificate for the server

    if rc == 0:
        rc = runCmd("keytool -genkeypair -storetype PKCS12 -keystore '{fn_keystore}' -storepass '{password}' -keypass '{password}' -alias '{server_alias}' -dname '{server_dn}' -validity '{age}' -keyalg RSA -keysize '{keysize}' -ext BasicConstraints:ca:false -file '{fn_tmp_keystore_csr}'")

    # Create a certificate signing request

    if rc == 0:
        rc = runCmd("keytool -certreq -keystore '{fn_keystore}' -storepass '{password}' -keypass '{password}' -alias '{server_alias}' -rfc -file '{fn_tmp_keystore_csr}'")

    # Sign the CSR with the CA certificate

    if rc == 0:
        rc = runCmd("keytool -gencert -keystore '{fn_tmp_catrust}' -storepass '{password}' -alias '{ca_alias}' -rfc -ext KeyUsage:critical=digitalSignature,keyEncipherment -ext ExtendedKeyUsage=serverAuth {extflags} -infile '{fn_tmp_keystore_csr}' -outfile '{fn_tmp_keystore_pem}'")

    # Import both the entire certificate chain into the keystore (starting with the root/CA certificate)

    if rc == 0:
        rc = runCmd("keytool -importcert -keystore '{fn_keystore}' -storepass '{password}' -file '{fn_truststore_pem}' -noprompt -alias '{ca_alias}'")

    if rc == 0:
        rc = runCmd("keytool -importcert -keystore '{fn_keystore}' -storepass '{password}' -file '{fn_tmp_keystore_pem}' -noprompt -alias '{server_alias}'")

    # Generate the help lines

    helpLines = ["""
The following files were created:
   {fn_truststore} - A java keystore containing the generated CA certificate; it is
                protected by the password provided to the --password_ts flag.

   {fn_truststore_pem} - The CA certificate from the keystore in PEM format; useful
                for importing into browsers

   {fn_keystore}   - Java keystore containing the server certificate (along with
                the private key) signed by the generated CA certificate. This is
                protected by the password provided on the command line or
                the default value.
"""]

    return rc, helpLines

# Main entry point

def main():
    global settings

    rc = 0

    # Create a namespace for filenames, since these are merged with the settings
    # namespace later, use argparse's class for this.

    filenames = argparse.Namespace()

    filenames.fn_server_p12     = "server.p12"
    filenames.fn_server_crt     = "server.crt"
    filenames.fn_server_key     = "server.key"
    filenames.fn_ca_p12         = "client.p12"
    filenames.fn_ca_crt         = "client.crt"
    filenames.fn_tmp_ca_cnf     = "tmp-ca.cnf"
    filenames.fn_tmp_ca_key     = "tmp-ca.key"
    filenames.fn_tmp_server_ext = "tmp-server.ext"
    filenames.fn_tmp_server_cnf = "tmp-server.cnf"
    filenames.fn_tmp_server_key = "tmp-server.key"
    filenames.fn_tmp_server_csr = "tmp-server.csr"
    filenames.fn_tmp_server_crt = "tmp-server.crt"

    filenames.fn_keystore          = "keystore";
    filenames.fn_truststore        = "truststore";
    filenames.fn_truststore_pem    = "truststore.pem";
    filenames.fn_tmp_catrust       = "tmp-catrust";
    filenames.fn_tmp_keystore_csr  = "tmp-keystore.csr";
    filenames.fn_tmp_keystore_pem  = "tmp-keystore.pem";

    # See what version of Open SSL is being used

    haveIterFlag = False

    rc, output = getCmdOutput("openssl version")

    if rc != 0:
        print("OpenSSL doesn't appear to be installed")
    else:
        m = re.match("OpenSSL (?P<version>[^ ]+) .*", output)

        if m:
            version = m.group("version")

            if version < "1.0.1e":
                print("Warning: Very old version of OpenSSL (%s) - this code may not work" % version)
            elif version >= "3.0.0":
                haveIterFlag = True
                # Java does not support the PKCS12 files created by the 3.0.0 alpha code (Java
                # support for PKCS12 seems to be limited in any case). We may want to create
                # a JKS format file for Java if they don't get it resolved.
                print("TBD: Make sure this version works with Java")

        else:
            print("Unknown SSL version (%s)...trying my best" % output.strip())

    # Process arguments; anything invalid ends the program

    if rc == 0:
        description = """
This program generates a self signed certificate for a server and a CA
certificate for use with clients/browsers. After successful generation,
information on how to use the "output files will be displayed.

gencert requires the openssl tools to be installed and in the path and
was tested with openssl version 1.1.1. To verify the version of openssl run
the command:

   openssl version

NOTE: gencert creates output files with the same files on each run and will
      silently overwrite any existing files with the same names.
"""

        epilog="""
HINTS AND TIPS
--------------

   * The default certificate password is {password} - change it if required
     by your use case.

   * The organization name field of the certificate ({organization}) can be
     customized for services work.

   * The certificate age is just over 3 years. This is actually **TOO LONG** for
     modern web certificates, but was set assuming a typical 3 year release
     life cycle.

   * The client and server alias flags can be used to set "short" alias names
     that can be used with Java.

EXAMPLES
--------

Unless you set the organizational unit name directory, the the customer and product
flags are required, however in general specifying the name of the service is also
useful as it allows you to more easily tell where each certificate is used. For
example, to generate a certificate for the customer Kroger running the (fictional)
CHEC service "DB Status":

   ./gencert.py --customer Kroger --product CHEC --service "DB Status"

The customer, product, and service fields all get used to generate the organizational
unit name in the certificate (with each part being separated by a dash). If you wish
to specify this field directly use the --ou_name flag.

   ./gencert.py --ou_name "Set the OU name field directly"

To see the results of certificate creation, run:

   openssl x509 -in {fn_server_crt} -text

Or, to strip off some of the extra binary information

   openssl x509 -in {fn_server_crt} -text -certopt no_sigdump,no_pubkey | grep "^ "

Java will display X509/PEM certificates directly as well:

   keytool -printcert -file {fn_server_crt}

By default the certificate will be valid for servers running on the controllers
CC and DD. Specifically the "Subject Alternate Names" field of the certificate
will list the automatically generated "adxautonet" names for these two
controllers. This would be useful in accessing the a web server on the controller
from a terminal. However if you wish to access the server from a local web
browser using "localhost", then you can add the --host flag to add it. Note,
however that when you use the --ctrl or --hostname flags you must list ALL hosts
and controller IDs you wish to use, for example:

   ./gencert.py --customer RETAILER --product TGCP --service NGINX  --ctrl cc --ctrl dd --hostname localhost

DEBUGGING (using PEM certificates)

   Start a simple server with openssl:
      openssl s_server -key {fn_server_key} -cert {fn_server_crt} -www

   See if SSL connent works; The browser does more with respect to hostname verification:
      echo | openssl s_client -CAfile {fn_ca_crt} -showcerts -connect localhost:4433 | less

   Print a very brief overview of the certificate presented. Change the port number to 443 and
   you can query certificates from web servers.
      nmap -p 4433 --script ssl-cert localhost

""".format(password=DEFAULT_PASSWORD,
           organization=DEFAULT_ORGANIZATION,
           **vars(filenames))

        parser = argparse.ArgumentParser(description=description[1:],
                                         epilog=epilog[1:],
                                         formatter_class=argparse.RawDescriptionHelpFormatter,
                                         add_help = True)

        parser.add_argument("-v", "--verbose", default=False, action='store_true',
                            help="Be more verbose (print command lines, etc)")

        parser.add_argument("-q", "--quiet", default=False, action='store_true',
                            help="Be less verbose (don't print status or help at the end)")

        # Password for keys. This will be by necessity hardcoded SOMEWHERE on the system since
        # we're transmitting all code to load the server around during ASM and such. However
        # in most cases it's better to do this than send keys in the clear (and it's OBVIOUS
        # that they're keys).  At least change this from project to project

        parser.add_argument("--password", default=DEFAULT_PASSWORD,
                            help="Password to use to protect files")

        # Organization

        parser.add_argument("--organization", default=DEFAULT_ORGANIZATION,
                            help="Organization name. Default is %s" % DEFAULT_ORGANIZATION)

        # Allow the ou_name to be set directly

        parser.add_argument("--ou_name",
                            help="Set the organizational unit name of the certificate directly rather than concatenating the customer, product, and service " \
                            "names. The purpose of the organizational unit name (along with the organization name) is to identify the certificate when viewed " \
                            "in web browsers or by automated scan tools.")

        # Customer name - all keys should be customer specific

        parser.add_argument("--customer",
                            help="Customer name for this project; all keys must be unique per customer")

        # Identify the product and the server within the product. For best practice, all
        # servers should use a unique key. However you could use one key per set of
        # machines (i.e. controllers) if you're within a specific store.

        parser.add_argument("--product",
                            help="Product name (e.g. NGP)")

        parser.add_argument("--service", default=None,
                            help="Unique service name (e.g. NGINX). If you don't want to share keys, in general each service on a given " \
                            "host address SHOULD have it's own key, however it's required that the host name list be complete for all hosts using the key. " \
                            "Set this to a blank string if you want to use only the customer and product in the certificate.")

        # You can set or append to the list of host names here.

        parser.add_argument("--hostname", default=[], action='append',
                            help="Set the DNS hostname where the service is hosted. If a service using the server certificate is reachable via multiple " \
                            "host names or the service will be running on multiple machines, specify this flag multiple times. Usually the --ctrl flag or --term " \
                            "flags are more useful since that autogenerates most common names. If this flag is used in combination with the --ctrl/--term flags, " \
                            "these hostnames are appended to the list. This is useful for adding 'localhost', e.g. '-ctrl dg --ctrl dt --term 20-30 --hostname localhost'")

        # Add the controller id

        parser.add_argument("--ctrl", default=[], action='append',
                            metavar='id-[id]',
                            help="Auto-generate the common 4690 'hosts file' names for a given controller, adding hostname entries for each. The value must be " \
                            "a 2 letter controller id (role ids may be used as well). The default controller id list is: %s. When you use this flag, the default " \
                            "list is removed; specify this flag multiple times, once per controller, i.e. '-ctrl dg -ctrl dt'. If the parameter value contains a dash, " \
                            "it's treated like a range and all possible controller ids in that range added to the list. This may produce an excessively large SAN field " \
                            "in the certificate that may not be supported by all tools. Only the 'lan0' names are added when using a range." % DEFAULT_CONTROLLER_LIST)

        # Add a range of terminal numbers to the list. Store must also be specified

        parser.add_argument("--store",
                            help="Indicate the 4 character store number/id to be used when adding host names for terminals using the --term flag")

        parser.add_argument("--term", default=[], action='append',
                            metavar="start[-end]",
                            help="It's doubtful that terminals will need server certificates...but 'just in case', this flag may help. The argument for this " \
                            "flag is an individual terminal number (from 1 to 999) or a range of terminal numbers (e.g. 20-30). By default no terminal names " \
                            "are added. If you use this flag, the default controller list is removed and you must individually specify the controller names " \
                            "or other hostnames to add. Note that adding all terminals in the store ('--term 0-999') may result in a certificate that some " \
                            "tools cannot handle (the SAN field would be over 16K in size).")

        # Customer name - all keys should be customer specific

        parser.add_argument("--keep", default=False, action="store_true",
                            help="Do not erase temporary files")

        # Number of days until certificates expire

        parser.add_argument("--age", default=1200, type=int,
                            help="Certificate age in days")

        # Allow the SAN to be made non-critical in all cases

        parser.add_argument("--nosancrit", default=False, action="store_true",
                            help="Don't mark the x509 SAN as critical even with multiple hosts. This will allow older clients (browsers) to still load " \
                            "the certificate even if they do not understand that field, but will limit usage to only the first host/controller listed.")

        # Allow java alias to be set

        parser.add_argument("--ca_alias", default=None,
                            help="Specify the certificate nickname (Java alias) for the client/CA certificate. By "
                            "default will contain the value of the OU field along with the certificate type.")

        parser.add_argument("--server_alias", default=None,
                            help="Specify the certificate nickname (Java alias) for the server certificate. By "
                            "default will contain the value of the OU field along with the certificate type.")

        # Allow iterations to be set if on OpenSSL 3

        if haveIterFlag:
            parser.add_argument("--iterations", default=DEFAULT_ITER_COUNT, type=int,
                                help="Set the interation hash count for the MAC/key. The default %u. This is only supported in newer "
                                "versions of OpenSSL (in older versions the iteration count is fixed at 2048). Your version %s support "
                                "setting the iteration count." % (DEFAULT_ITER_COUNT, "does" if haveIterFlag else "DOES NOT"))

        # Allow CN to be set specifically for each certificate

        parser.add_argument("--server_cn",
                            help="Set the CN value for the server certificate. If at least one DNS name is listed in the SAN list, modern software "
                            "should ignore this field, so this could be set to anything. Older software may allow/expect a wildcard FQDN in this "
                            "field, but the practice is deprecated - see RFCs 2818 and 6125. By default this is set to the first DNS name listed in "
                            "the SAN field. WHEN USING THIS FLAG, it will ignore the default controller list. Thus, using this flag by itself will "
                            "create a certificate without the SAN extension; allowing you to create a certificate with only the CN field set (useful "
                            "in creating a cert with a wildcard CN for older software). If you use this flag with the --ctrl/--hostname flags, it will "
                            "create a cert with the SAN extension. This allows you to put a text description in CN (which modern programs should ignore) "
                            "or a wildcard FQDN for use with older software too. In the later case, use the --nosancrit flag to mark the SAN as "
                            "non-critical, allowing older software to ignore the section.")

        parser.add_argument("--ca_cn",
                            help="Set the CN value for the client (CA) certificate. Set to descriptive text that includes the OU by default.")

        # Allow keysize to be set

        parser.add_argument("--keysize", default=DEFAULT_KEYSIZE, type=int,
                            help="Set the keysize used; default is %u bits" % DEFAULT_KEYSIZE)

        # Allow java certificates to be used

        parser.add_argument("--usejava", default=False, action="store_true",
                            help="Use java to generate the certificates; generate both a key store and a trust store. The key and store password for each "
                            "are set to the value set by the --password flag")

        parser.add_argument("--password_ts", default=None,
                            help="The password used to protect the java truststore. The password provided to the --password flag used to protect the keystore ONLY. "
                            "Since java requires a password and the truststore password realistically be different than the keystore password, this parameter is "
                            "required")

        # Process the arguments

        args = sys.argv[1:]

        if not args:
            print("Used to generate certificate files in PKCS12 and PEM formats\n")
            parser.print_usage()
            print("\nUse the -h or --help flag for more detailed information")
            sys.exit(1)
        else:
            settings = parser.parse_args(args=args)

            # Verbose wins over quiet

            if settings.verbose:
                settings.quiet = False

    # Add the client filenames to the settings object so they can be used with
    # help and commands. We can add flags with the same variable names if desired
    # to override any filename we wish.

    for var in vars(filenames):
        if not var in settings:
            setattr(settings, var, getattr(filenames, var))

    # Set defaults for things if the user did not
    # **************************************************************************

    # Skip any code that sets iterations, using the default

    if not haveIterFlag or settings.usejava:
        settings.iterations = 0

    # The customer set the ou_name field or must pass the product and customer
    # flags. If ou_name is not set, product and customer must be non-blank

    if not settings.ou_name:
        if not settings.customer or not settings.product:
            print("Error: You must set both the customer and product if not setting ou_name")
            rc = 1
        else:
            settings.ou_name = settings.customer+" - "+settings.product+(" - "+settings.service if settings.service else "")

    # Fill in a few fields based on OU name

    if rc == 0:
        # Give the certificate a name

        if not settings.ca_alias:
            settings.ca_alias = settings.ou_name+" CA Certificate"

        if not settings.server_alias:
            settings.server_alias = settings.ou_name+" Server Certificate"

        # The CN value in the CA should not necessarily be a FQDN as with
        # the cert presented by the server.

        if not settings.ca_cn:
            settings.ca_cn = settings.ou_name+" CA"

    # Generate the list of hostnames to use in the SAN

    if rc == 0:
        # If the user gave us neither controller nor terminal addresses, use
        # the default, otherwise use exactly what we were told

        if not settings.hostname and not settings.ctrl and not settings.term and not settings.server_cn:
            settings.ctrl = DEFAULT_CONTROLLER_LIST

        # The settings.hostname field will always contain our host list, however
        # since hostnames are likely things like localhost, put those at the end.
        #
        # The ONLY affect this really has is that our code below uses the first
        # name in the list as the CN.

        argHostNames = settings.hostname
        settings.hostname = []

        # Add controllers

        if settings.ctrl:
            for ctrl in settings.ctrl:
                ctrl = ctrl.lower()

                if re.match("[a-z][a-z]-[a-z][a-z]", ctrl):
                    start1 = ord(ctrl[0])
                    start2 = ord(ctrl[1])
                    end1 = ord(ctrl[3])
                    end2 = ord(ctrl[4])

                    if start1 > end1 or start2 > end2:
                        print("Error: Invalid controller range: %s" % ctrl)
                        rc = 1
                        break

                    for c1 in range(start1, end1+1):
                        for c2 in range(start2, end2+1):
                            for prefix in [ "lan0" ]:
                                settings.hostname.append("%s.adxlx%c%cn.adxautonet" % (prefix, chr(c1), chr(c2)))

                elif re.match("[a-z][a-z]", ctrl):
                    # Note that RFC 6125 says the wildcard matching is not supported. Other
                    # specifications like PKIX say they are...and they're apparently used by
                    # browsers. So we can add or use them if needed.
                    #
                    # See https://tools.ietf.org/html/rfc6125

                    for prefix in [ "lan0", "lan1" ]:
                        settings.hostname.append("%s.adxlx%sn.adxautonet" % (prefix, ctrl))
                else:
                    print("Error: Invalid controller ID or id range: %s" % ctrl)
                    rc = 1
                    break

        # Add terminals

        if settings.term:
            if not settings.store:
                print("Store name not set")
                rc = 1
            elif not re.match("[0-9A-Za-z]{4}", settings.store):
                print("Store id invalid")
                rc = 1
            else:
                for termRange in settings.term:
                    # Determine start/end of the range

                    isRange = termRange.find("-") >= 0
                    badVal = None

                    if not isRange:
                        try:
                            start = end = int(termRange)
                        except ValueError:
                            badVal = termRange
                    else:
                        start, end = termRange.split("-", 2)

                        try:
                            start = int(start)
                        except ValueError:
                            badVal = start
                        try:
                            end = int(end)
                        except ValueError:
                            badVal = end

                    # Validate range

                    if badVal is None:
                        if start < 1 or start > 999:
                            badVal = start
                        elif end < 1 or end > 999:
                            badVal = end
                        elif start > end:
                            badVal = termRange

                    # Add if ok, fail otherwise

                    if badVal is not None:
                        print("Invalid terminal %s: %s" % ("range" if isRange else "number", badVal))
                        rc = 1
                        break
                    else:
                        for term in range(start,end+1):
                            settings.hostname.append("T%s%03u" % (settings.store.upper(), term))


        # Append hostnames

        if argHostNames:
            settings.hostname.extend(argHostNames)

    # Add properties for alternate names
    #
    # This code allows for IP addresses AND DNS names. The original RFC 2818
    # allowed for both but a later one RFC 6125 only supports only DNS names
    # for newer apps(?).

    if rc == 0:
        settings.altNames = []

        numDNS = 0
        numIP = 0

        # Lowercase all host names and remove dups

        newHostList = []

        for name in settings.hostname:
            name = name.lower()
            if name not in newHostList:
                newHostList.append(name)

        settings.hostname = newHostList

        # Host names components can contain ASCII letters, digits, and the underscore, but
        # must not start or end with an underscore (RFC1123). Two or more components can
        # may be provided, separated with a period.  If you require host names containing
        # unicode characters, they must be translated via nameprep/punycode into a name
        # meeting RFC 3490 requirements - https://en.wikipedia.org/wiki/Internationalized_domain_name
        # This code allows xn-- style names for this reason.

        ipAddrRegex = re.compile("^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        hostNameRegex = re.compile("^(xn--){0,1}(([a-z0-9]|[a-z0-9][a-z0-9-]*[a-z0-9])\.)*([a-z0-9]|[a-z0-9][a-z0-9\-]*[a-z0-9])$", re.IGNORECASE)

        for name in settings.hostname:
            if ipAddrRegex.match(name):
                settings.altNames.append("IP.%u = %s" % (numIP, name))
                numIP += 1
            elif not hostNameRegex.match(name):
                print("Error: %s is neither an IP address nor host name" % name)
                rc = 1
            else:
                settings.altNames.append("DNS.%u = %s" % (numDNS, name))
                numDNS += 1

                # Set the common name to the first DNS name; there must be at least one
                if not settings.server_cn:
                    settings.server_cn = name

        settings.altNames.sort()

        # If there was more than one ip/dns name, mark the SAN as critical

        settings.san_critical = numIP+numDNS > 1 and not settings.nosancrit

        # If using the SAN at least one name must be a DNS name to be a valid
        # web certificate. Using only IP addresses is possible, but in general
        # will fail audits/etc so there is no option to override this.

        if not rc and not numDNS:
            # There IS a special case of this. If there is no SAN list and the
            # user specifically set the server CN, they may be generating a
            # simple cert with a wildcard name....so we allow it

            if not settings.altNames and settings.server_cn:
                pass
            else:
                print("Error: At least one hostname must be an DNS address")
                rc = 1

    # All the input is valid...we should be good from here

    if rc == 0:
        if settings.usejava:
            rc, helpLines = genCertJava()
        else:
            rc, helpLines = genCertOpenSSL()

    # Clean temporary files...the client and server files should be all that's needed

    if 0 == rc and not settings.keep:
        tmpFiles = [ getattr(settings, v) for v in vars(settings) if v.startswith("fn_tmp_") ]

        for fn in [fn for fn in tmpFiles if os.path.exists(fn)]:
            os.remove(fn)
            if settings.verbose:
                print("Removed: %s" % fn)

    if rc == 0 and not settings.quiet:
        print("\n".join(helpLines).format(**vars(settings)))

    print("FAILURE" if rc else "SUCCESS")

    return rc

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print("Error running program: %s" % e)
        traceback.print_exc()
        sys.exit(99)
