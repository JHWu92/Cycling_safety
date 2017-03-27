<?php
    use PHPUnit\Framework\TestCase;
    include_once(dirname(__FILE__).'/../check-login.php');
    include_once(dirname(__FILE__).'/../config.inc.php');
    
    class LoginTest extends TestCase
    {

        /**
        * @dataProvider loginFalseProvider
        **/
        public function testLoginFalse($sess_data)
        {   
            $this->assertFalse(login($sess_data));
        }
        
        public function loginFalseProvider(){
            
            return array(
                array(
                    array($GLOBALS['SESS_USER_ID']=>123, $GLOBALS['SESS_EMAIL'] => 'new@g.com', $GLOBALS['SESS_LOGIN']=>False),
                    'foo',
                ),
            );
        }       
        
        /**
        * @dataProvider loginTrueProvider
        **/
        public function testLoginTrue($sess_data)
        {   
            $this->assertTrue(login($sess_data));
        }
        
        public function loginTrueProvider(){
            
            return array(
                array(
                    array($GLOBALS['SESS_USER_ID']=>123, $GLOBALS['SESS_EMAIL'] => 'new@g.com', $GLOBALS['SESS_LOGIN']=>True),
                    'foo',
                ),
            );
        }
        
 
        
    }
?>
