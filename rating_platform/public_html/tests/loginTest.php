<?php
require 'DBFixture.php';
require dirname(__FILE__).'/../emailExpSurveyDBandRedirect.php';
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
        # No modification on existing DB
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        # correct URL
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_SURVEY'], $res['head_url']);
        # correct user_id
        $this->assertEquals(2, $res[$GLOBALS['SESS_USER_ID']]);
        # correct exp lvl
        $this->assertEquals('Fearless', $res[$GLOBALS['SESS_EXPLV']]);
        # correct has no survey
        $this->assertNull($res[$GLOBALS['SESS_SURVEY']]);
    }
    
    public function testHasSurvey(){
        # T6
        $conn = $this->getConnection();
        $email = 'has-survey@g.com';
        $res = handle_input_email(self::$pdo, $email);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        # No modification on existing DB
        $expectedTable = $this->getDataSet()->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        # correct URL
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
        # correct user_id
        $this->assertEquals(3, $res[$GLOBALS['SESS_USER_ID']]);
        # correct exp lvl
        $this->assertEquals('Interested', $res[$GLOBALS['SESS_EXPLV']]);
        # correct has survey
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
    
    public function testSaveSurvey(){
        # T9
        $conn = $this->getConnection();
        $user_id = 2;
        $post_data = array(
            $GLOBALS['TB_U_COL_BK_PURPOSE']=>1,
            $GLOBALS['TB_U_COL_GENDER']=>2,
            $GLOBALS['TB_U_COL_DRIVER']=>1,
            $GLOBALS['TB_U_COL_BK_TYPE']=>4,
        );
        $res = handle_survey(self::$pdo, $user_id, $post_data);
        $queryTable = $conn->createQueryTable('Users', 'SELECT * FROM Users');
        # update survey correctly
        $expectedTable = $this->getDataSet('updateSurveyUsers')->getTable('Users');
        $this->assertTablesEqual($expectedTable, $queryTable);
        $this->assertEquals("Location: ".$GLOBALS['DOMAIN_URL'].$GLOBALS['PAGE_RATE_VIDEO'], $res['head_url']);
    }
    
    public function testLoginLog(){
        # T21
        $conn = $this->getConnection();
        $user_agent = 'agent4';
        $data = array(
            [1, '2017-03-28 10:16:28', 'GMT -4', $user_agent, '', '', '', ''],
            [3, '2017-03-28 12:16:28', 'GMT -4', $user_agent, 1, '', 1, ''],
            [2, '2017-03-28 22:18:38', 'GMT -4', $user_agent, 1, 1, 1, ''],
            [3, '2017-03-28 22:20:48', 'GMT -4', $user_agent, 1, '', '', 1],
        );
        foreach($data as $login){
            logLogin(self::$pdo, $login[0], $login[1], $login[2], $login[3], $login[4], $login[5], $login[6], $login[7]);
        }
        $queryTable = $conn->createQueryTable('loginLog', 'SELECT * FROM loginLog');
        # update survey correctly
        $expectedTable = $this->getDataSet('loginLog')->getTable('loginLog');
        $this->assertTablesEqual($expectedTable, $queryTable);
        
    }
}
?>