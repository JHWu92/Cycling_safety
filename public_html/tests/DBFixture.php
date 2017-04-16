<?php
use PHPUnit\Framework\TestCase;
use PHPUnit\DbUnit\TestCaseTrait;
/**
 * These are required to ensure that the PDO object in the class is able to work correctly
 * @backupGlobals disabled
 * @backupStaticAttributes disabled
 */
class DBFixtureTestCase extends TestCase
{
    use TestCaseTrait;

    /**
     * only instantiate pdo once for test clean-up/fixture load
     * @var PDO
     */
    static protected $pdo = null;

    /**
     * only instantiate PHPUnit_Extensions_Database_DB_IDatabaseConnection once per test
     * @var type 
     */
    private $conn = null;
    
    public static function tearDownAfterClass()
    {
        self::$pdo = null;
    }

    protected function getConnection()
    {
        if ($this->conn === null) {
            if (self::$pdo == null) {
                self::$pdo = new PDO($GLOBALS['DB_DSN'], $GLOBALS['DB_USER'], $GLOBALS['DB_PASSWD']);
                //fwrite(STDOUT, "get pdo\n");
            }
            $this->conn = $this->createDefaultDBConnection(self::$pdo, $GLOBALS['DB_DBNAME']);
        }
        return $this->conn;
    }
    
    public function setUp() {
        //fwrite(STDOUT, "setUp\n");
        
    	$conn = $this->getConnection();
        $allTables = $this->getDataSet()->getTableNames();
        foreach ($allTables as $table) {
        	// drop table
        	$conn = $this->getConnection();
        	self::$pdo->exec("TRUNCATE `$table`;");
        }
        //fwrite(STDOUT, "cleared table\n");
        // set up tables
        $fixtureDataSet = $this->getDataSet();
        $this->loadDataSet($fixtureDataSet);
        parent::setUp();
    }
    public function tearDown() {
        //fwrite(STDOUT, "tearDown\n");
        $allTables = $this->getDataSet()->getTableNames();
        foreach ($allTables as $table) {
        	// drop table
        	$conn = $this->getConnection();
        	#self::$pdo->exec("TRUNCATE `$table`;");
        }
        parent::tearDown();
    }
    public function loadDataSet($dataSet) {
        
        //fwrite(STDOUT, "loadDataSet\n");
        // set the new dataset
        $this->getDatabaseTester()->setDataSet($dataSet);
        // call setUp whateverhich adds the rows
        $this->getDatabaseTester()->onSetUp();
    }
    
    protected function getDataSet($filename='')
    {   
        if ($filename == '') {
			$filename = 'fixtures';
		}
        //fwrite(STDOUT, "getDataSet, $filename\n");
        return $this->createMySQLXMLDataSet(dirname(__FILE__)."/test_data/$filename.xml");
    }

}