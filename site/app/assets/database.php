<?php

class Database {
	
	private $connection;

	private $dbAddress = "127.0.0.1";
	private $dbUsername = "scripts";
	private $dbPassword = "scripts";
	private $dbSchema = "sentiment";

	function __construct() {}

	function connect() {
		
		try {
			if(!$this->connection) {
				$this->connection = mysqli_connect($this->dbAddress, $this->dbUsername, $this->dbPassword, $this->dbSchema);
				if (!$this->connection) {
					echo mysql_error($this->connection);
					return "0";
				}
			}
		} catch (Exception $e) {
			return "0";
		}

		return "1";
	}

	function disconnect() {
		mysqli_close($this->connection);
	}

	function getCurrentBatch() {

		$this->connect();

		$query = "select max(id) from result_batch;";

		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}

	function getOverallSentiment($currentBatch) {

		$this->connect();

		$query = "select positive, negative from result where result_batch_id = " . $currentBatch . " and result_type_id = 8;";
		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0], $row[1]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}

	function getTrending($currentBatch) {

		$this->connect();

		$query = "select description, positive from result where result_batch_id = " . $currentBatch . " and result_type_id = 1;";
		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0], $row[1]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}

	function getNumberOfThreads($currentBatch) {

		$this->connect();
		
		$query = "select positive from result where result_batch_id = " . $currentBatch . " and result_type_id = 4;";
		if ($result = mysqli_query($this->connection, $query)) {

			$count = "";

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$count = $row[0];
				break;
			}
			mysqli_free_result($result);
			
			return $count;
		}

		$this->disconnect();
		
		return false;
	}

	function getTeams($currentBatch) {

		$this->connect();

		$query = "select description, positive, negative from result where result_batch_id = " . $currentBatch . " and result_type_id = 5 order by positive desc;";
		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0], $row[1], $row[2]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}

	function getPlayers($currentBatch) {

		$this->connect();

		$query = "select description, positive, negative from result where result_batch_id = " . $currentBatch . " and result_type_id = 6 order by positive desc;";
		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0], $row[1], $row[2]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}

	function getChampions($currentBatch) {

		$this->connect();

		$query = "select description, positive, negative from result where result_batch_id = " . $currentBatch . " and result_type_id = 7 order by positive desc;";
		if ($result = mysqli_query($this->connection, $query)) {

			$rows = array();

			$i = 0;
			while ($row = mysqli_fetch_row($result)) {
				$rows[$i] = array($row[0], $row[1], $row[2]);
				$i++;
			}
			mysqli_free_result($result);

			return $rows;
		}

		$this->disconnect();
		
		return false;
	}
}

?>