<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../DBandRedirect.php';
include_once(dirname(__FILE__).'/../config.inc.php');
class loginTest extends DBFixtureTestCase{

    public function testNewUser(){
        # T3
        $conn = $this->getConnection();
        $email = 'new@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet('inserNewUsers')->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_EXP'], $res['head_url']);
        $this->assertEquals(4, $res[$GLOBALS['SESS_USER_ID']]);
        $this->assertNull($res[$GLOBALS['SESS_EXPLV']]);
        $this->assertNull($res[$GLOBALS['SESS_SURVEY']]);
    }
    
    public function testNoExp(){
        # T4
        $conn = $this->getConnection();
        $email = 'no-exp@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_EXP'], $res['head_url']);
        $this->assertEquals(1, $res[$GLOBALS['SESS_USER_ID']]);
        $this->assertNull($res[$GLOBALS['SESS_EXPLV']]);
        $this->assertNull($res[$GLOBALS['SESS_SURVEY']]);
    }
    
    public function testNoSurvey(){
        # T5
        $conn = $this->getConnection();
        $email = 'no-survey@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SURVEY'], $res['head_url']);
        $this->assertEquals(2, $res[$GLOBALS['SESS_USER_ID']]);
        $this->assertEquals('Fearless', $res[$GLOBALS['SESS_EXPLV']]);
        $this->assertNull($res[$GLOBALS['SESS_SURVEY']]);
    }
    
    public function testHasSurvey(){
        # T6
        $conn = $this->getConnection();
        $email = 'has-survey@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        $this->assertEquals(3, $res[$GLOBALS['SESS_USER_ID']]);
        $this->assertEquals('Interested', $res[$GLOBALS['SESS_EXPLV']]);
        $this->assertEquals(1, $res[$GLOBALS['SESS_SURVEY']]);
    }
    
    public function testUpdateExp(){
        # T7
        $conn = $this->getConnection();
        $user_id = 1;
        $has_survey = Null;
        $explv = 'Interested';
        $res = handle_exp_lvl(self::$pdo, $user_id, $has_survey, $explv);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        $expectedTable = $this->getDataSet('updateUsers')->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SURVEY'], $res['head_url']);
        
        $has_survey = 1;
        $res = handle_exp_lvl(self::$pdo, $user_id, $has_survey, $explv);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        
    }

}
?>