import urllib2
import sys

dataSnap = """
<script>
      <scriptName>jsnap-snapshot.slax</scriptName>
      <scriptContents><![CDATA[

\/* @ISLOCAL="true" *\/
\/* @PASSDEVICECREDENTIALS="true" *\/
version 1.0;

ns junos = "http://xml.juniper.net/junos/*/junos";
ns xnm = "http://xml.juniper.net/xnm/1.1/xnm";
ns jcs = "http://xml.juniper.net/junos/commit-scripts/1.0";

ns exsl extension = "http://exslt.org/common";
ns dyn extension = "http://exslt.org/dynamic";
ns func extension = "http://exslt.org/functions";
ns date extension = "http://exslt.org/dates-and-times";

ns jfile = "http://xml.juniper.net/jawalib/libjfile";
ns cbd = "http://xml.juniper.net/jawalib/libcbd";

ns jppc = "http://xml.juniper.net/jppc";

import "/usr/jawa/lib/libxns.slax";
import "/usr/jawa/lib/libjfile.slax";
import "/usr/jawa/lib/libcbd.slax";
import "/usr/jawa/jsnap/jppc-utils.slax";

var $CONF-FILE = "/usr/jawa/jsnap/samples/sample.conf";
var $SNAP-NAME = date:seconds();
var $SECTION;
var $splitCreds = jcs:split("(@)", $credentials);
var $ipAndPassword= jcs:split("(\\\\:)", $splitCreds[2]);
var $USER = $splitCreds[1];
var $PASSWD = $ipAndPassword[2];
var $TARGET = $ipAndPassword[1];
var $TARGET-FILE;

var $arguments = {
    <argument> {
        <name> "Pre_or_Post_Snap";
        <description> "Determines whether this is the pre or post snapshot";
    }
}

var $TIME-NOW = date:date-time();

var $jfile:JUNOS = false();

match / {


    var $ini-file = cbd:read( $CONF-FILE );
    if( $ini-file/cbd:error ) {
        for-each( $ini-file/cbd:error ) {
            expr jcs:output( "ERROR[", file, "]: ", message );
        }
        <xsl:message terminate="yes"> "Exiting.";
    }

    var $section-cmd-ns = jppc:section( $ini-file );

    if( $SECTION ) {
        if(not( $section-cmd-ns )) {
            expr jcs:output("ERROR: Could not find: '", $SECTION, "' in config file '", $CONF-FILE, "' !" );
            <xsl:message terminate="yes">;
        }
    }

    var $targets = jppc:targets();
    if(not( $targets )) {
       expr jcs:output("ERROR: no TARGET or TARGET-FILE defined !");
       <xsl:message terminate="yes">;
    }

   var $passwd = {
       call get_passwd($PASSWD);
   }

   if(not($USER) || not($passwd)) {
      <xsl:message terminate="yes"> "You must specify 'USER' and 'password'";
   }

   for-each( $targets ) { var $target = string(.);
      call do_snapshot( $ini-file, $target, $passwd, $section-cmd-ns );
   }
}

template do_snapshot( $ini-file, $target, $passwd, $section-cmd-ns )
{
   expr jcs:output("Connecting to ", $USER, "@", $target, " ... ");
    var $jnx = jcs:open( $target, $USER, $passwd );
    if(not( $jnx )) {
       expr jcs:output("Unable to connect to device: ", $target, " ... SKIPPING! ");
    }
    else {
       expr jcs:output("CONNECTED.");

       if( $section-cmd-ns ) {
          call do_junos_cmd( $jnx, $target, $cmd-ns = $section-cmd-ns );
       }
       else {
          for-each( $ini-file/do/child::* ) {
             var $child = name(.);
             var $cmd-ns = dyn:evaluate( "$ini-file/" _ $child );
             if(not( $cmd-ns )) {
                expr jcs:output("ERROR: [" _ $CONF-FILE _ "]: Could not find: ", $child, " ... SKIPPING!" );
             }
             else {
                call do_junos_cmd( $jnx, $target, $cmd-ns );
             }
          }
       }

       expr jcs:close( $jnx );
    }
}

template do_junos_cmd( $jnx, $target, $cmd-ns )
{
    var $cmd-name = name( $cmd-ns );
    var $filename = concat( $target, "__", $cmd-name,"__", $SNAP-NAME, ".xml" );

    expr jcs:output( "EXEC: '", $cmd-ns/command, "' ... ");

    var $rpc-cmd = <command> $cmd-ns/command;
    var $rpc-rsp = jcs:execute-xns( $jnx, $rpc-cmd );

    if( $rpc-rsp/xnm:error ) {
        expr jcs:output("ERROR: [invalid Junos command]: '", $cmd-ns/command, "'" );
    }
    else {
        expr jcs:output( "SAVE: '", $filename, "' ... ");
        <exsl:document href=$filename indent="yes"> {
            <jppc:section name=$cmd-name mode=$SNAP-NAME conf=$CONF-FILE target=$target ts=$TIME-NOW> {
                copy-of $rpc-rsp/*;
            }
        }
    }
}

template get_passwd($PASSWD)
{
   if ($PASSWD) {
       expr $PASSWD;
   }
   else {
       var $passwd = jcs:get-secret( $USER _ " password: ");
       expr $passwd;
   }
}

      ]]></scriptContents>
</script>
"""


req = urllib2.Request("https://"+sys.argv[1]+"/api/space/script-management/scripts", dataSnap)

req.add_header('Authorization', 'Basic ' + sys.argv[2])
req.add_header('Content-Type', 'application/vnd.net.juniper.space.script-management.script+xml;version=1;charset=UTF-8')

response = urllib2.urlopen(req)
