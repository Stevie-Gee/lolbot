<?php
// ####################### SET PHP ENVIRONMENT ###########################
error_reporting(E_ALL & ~E_NOTICE & ~8192);

/* This script only allows connections over SSL, via POST.
 * It takes a password and user parameter, and queries the database for any
 * users matching the given user. If a match is found, returns some info
 * about the user. Any failure (e.g. incorrect password, user unknown) returns
 * an empty string.
 */ 

// Safety checks
if (($_SERVER["REQUEST_METHOD"] != "POST") || !(isset($_SERVER["HTTPS"]))){
    die("");
}
if ($_POST["password"] != "iJ9xls4qa4ZU9lXHGM5vxGEmNHLmmIeg") {
    die("");
}

include "./includes/config.php";
$link = mysql_connect($config['MasterServer']['servername'] ,
                      $config['MasterServer']['username'], 
                      $config['MasterServer']['password']);
if (!$link) {
    die("");
}
mysql_select_db($config['Database']['dbname']);

if($_POST["user"]){
    // "user" means this is a user search
    $user = mysql_real_escape_string($_POST["user"]);
    $query = mysql_query("SELECT username, usergroupid, userid, usertitle, joindate, posts, reputation FROM mst_user WHERE username=\"$user\"");
    if (!$query) {
        die("");
    }
    if (mysql_num_rows($query) === 0) {
        die("");
    }

    $result = mysql_fetch_row($query);
    foreach ($result as $key => $value){
        echo mysql_field_name($query, $key)." $value\n";
    }
}

elseif($_POST["quote"]) {
    // "quote" means we're doing something with a quote
    if($_POST["quote"] == "random") {
        // Return a random quote from the database
        $query = mysql_query("SELECT * FROM irc_quotes ORDER BY RAND() LIMIT 1");
    }
    elseif($_POST["quote"] == "get") {
        // Run a couple of searches to try and find some quotes
        if($_POST["id"]) {
            // Search by ID
            $id = mysql_real_escape_string($_POST["id"]);
            $query = mysql_query("SELECT * FROM irc_quotes WHERE id=$id");
        }
        elseif($_POST["text"]) {
            // Do a text search (or two)
            $text =  mysql_real_escape_string($_POST["text"]);
            
            // This regex matches a word (i.e. surrounded by spaces)
            // To prevent a search for "some guy" giving results for "I have some things for this guy"
            // Also note that a FULLTEXT search won't index short words
            $query = mysql_query("SELECT * from irc_quotes WHERE quote REGEXP \"[[:<:]]$text"."[[:>:]]\" ORDER BY RAND() LIMIT 5");
            
            // If that didn't work, do a normal FULLTEXT search
            if (mysql_num_rows($query) === 0) {
                $query = mysql_query("SELECT * from irc_quotes WHERE MATCH(quote) AGAINST(\"$text\") ORDER BY RAND() LIMIT 5");
            }
        }
    }
    
    elseif($_POST["quote"] == "delete") {
        //Delete the requested quote and then exit
        $id = mysql_real_escape_string($_POST["id"]);
        $query = mysql_query("DELETE FROM irc_quotes WHERE id=$id");
        if ( mysql_affected_rows() > 0) {
            echo "Success";
            exit();
        } else {
            die("");
        }
    }
    
    elseif($_POST["quote"] == "add") {
        //Add a new quote to the database
        $nick = mysql_real_escape_string($_POST["nick"]);
        $host = mysql_real_escape_string($_POST["host"]);
        $channel = mysql_real_escape_string($_POST["channel"]);
        $text = mysql_real_escape_string($_POST["text"]);
        $query = mysql_query("INSERT INTO irc_quotes (nick, host, channel, quote) VALUES (\"$nick\", \"$host\", \"$channel\", \"$text\")");
        
        if (!$query) {
            die("");
        }
        // Get the quote ID and return it
        $query = mysql_query("SELECT id from irc_quotes ORDER BY id DESC LIMIT 1");
        echo mysql_fetch_row($query)[0];
        exit();
    }
    
    // Parse the search results (if any)
    if (!$query || mysql_num_rows($query) === 0) {
        die("");
    }
    while ($row = mysql_fetch_assoc($query)) {
        foreach ($row as $key => $value) {
            echo "$key $value\n";
        }
        echo "\n";
    }
}
?>
