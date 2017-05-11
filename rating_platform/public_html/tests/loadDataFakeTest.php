<?php
use PHPUnit\Framework\TestCase;
use PHPUnit\DbUnit\TestCaseTrait;

class loadDataFakeTest extends TestCase
{
    use TestCaseTrait;

 
    static protected $pdo = null;

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
        fwrite(STDOUT, "setUp\n");
        
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

    }
    public function loadDataSet($dataSet) {
        
        $this->getDatabaseTester()->setDataSet($dataSet);
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
    
    public function testPushAndPop()
    {
        $stack = [];
        $this->assertEquals(0, count($stack));

        array_push($stack, 'foo');
        $this->assertEquals('foo', $stack[count($stack)-1]);
        $this->assertEquals(1, count($stack));

        $this->assertEquals('foo', array_pop($stack));
        $this->assertEquals(0, count($stack));
    }

}