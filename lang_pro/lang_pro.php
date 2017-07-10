<?php
    $path = [
        'lib' => '../../lib',
        'account' => '../../account/'.$argv[2],
        'app_lib' => '../../account/'.$argv[2].'/lib/lang_pro'
    ];
    $f_require = [
        $path['lib'].'/twitteroauth/autoload.php',
        $path['lib'].'/twitteroauth/src/TwitterOAuth.php',
        $path['account'].'/config.php'
    ];
    foreach ($f_require as $f) require $f;
    use Abraham\TwitterOAuth\TwitterOAuth;

    class lang_pro{
        private $path, $file, $u_list;
        function __construct($path){
            $this->path = $path;
            $this->file = [
                'usr' => $path['app_lib'].'/usr_list.txt',
                't_list' => $path['app_lib'].'/tweet_list.txt',
                'containts' => $path['app_lib'].'/tweet_containts.txt'
            ];
        }
        private function get_u_list(){
            $fpr = fopen($this->file['usr'], 'r');
                while ($id = fgets($fpr)) $this->u_list[] = explode(' ', $id);
            fclose($fpr);
        }
        private function get_connection(){
            return new TwitterOAuth(consumer_key, consumer_secret, access_token, access_token_secret);
        }
        private function get_tweet($usr){
            $connection = $this->get_connection();
            $timeline = $connection->get('statuses/user_timeline', ['screen_name' => $usr[0], 'count' => 100]);
            if ($timeline[0]->id > $usr[1]){
                foreach ($timeline as $tl) {
                    if ($tl->id <= $usr[1]) break;
                    file_put_contents($this->file['t_list'], '\{'.PHP_EOL.$tl->text.PHP_EOL.'\}'.PHP_EOL, FILE_APPEND);
                }
            }
            file_put_contents($this->file['usr'], $usr[0].' '.$timeline[0]->id.PHP_EOL, FILE_APPEND);
        }
        public function make_t_list(){
            $this->get_u_list();
            unlink($this->file['usr']);
            file_put_contents($this->file['t_list'], '');
            foreach ($this->u_list as $usr) $this->get_tweet($usr);
        }
        public function tweet(){
            $connection = $this->get_connection();
            $message = file_get_contents($this->file['containts']);
            $request = $connection->post('statuses/update', array('status'=>$message));
        }
    }

    $lang_pro = new lang_pro($path);
    switch ($argv[1]){
        case 'get_tweet':
            $lang_pro->make_t_list(); break;
        case 'tweet':
            $lang_pro->tweet(); break;
    }
?>
