<?php
	echo "Server: " . php_uname('n') . "<br>";
	echo "PHP: "    . phpversion()   . "<br>";
	echo "Time: "   . date('Y-m-d H:i:s') . "<br>";
	echo "IP: "     . $_SERVER['SERVER_ADDR'];
?>
