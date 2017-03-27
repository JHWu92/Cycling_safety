<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../checkEmail.php';
include_once(dirname(__FILE__).'/../config.inc.php');
class loginTest extends DBFixtureTestCase{

    public function testNewUser(){
        $conn = $this->getConnection();
        $email = 'new@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet('inserNewUsers')->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_EXP'], $res['head_url']);
        $this->assertEquals(4, $res[$GLOBALS['SESS_USER_ID']]);
    }
    
    public function testNoExp(){
        $conn = $this->getConnection();
        $email = 'no-exp@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_EXP'], $res['head_url']);
        $this->assertEquals(1, $res[$GLOBALS['SESS_USER_ID']]);
    }
    
    public function testNoSurvey(){
        $conn = $this->getConnection();
        $email = 'no-survey@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SURVEY'], $res['head_url']);
        $this->assertEquals(2, $res[$GLOBALS['SESS_USER_ID']]);
    }
    
    public function testHasSurvey(){
        $conn = $this->getConnection();
        $email = 'has-survey@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        $this->assertEquals(3, $res[$GLOBALS['SESS_USER_ID']]);
    }

}
?>