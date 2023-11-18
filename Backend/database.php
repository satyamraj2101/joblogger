<?php
$servername = "sql12.freesqldatabase.com";
$username = "sql12662911";
$password = "PSqhR4Tpuz";
$database = "sql12662911";

// Create connection
$conn = new mysqli($servername, $username, $password, $database);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

echo "Connected successfully";
?>
