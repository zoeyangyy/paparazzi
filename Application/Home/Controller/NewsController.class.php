<?php
namespace Home\Controller;
use Think\Controller;

class NewsController extends Controller {
	public function php(){
		echo phpinfo();
		$this->display();
	}
    public function index(){   	
    	header("Content-type: text/html; charset=utf-8");
    	$keywordany = $_POST["keyword-any"];
    	$keywordcom = $_POST["keyword-company"];
    	$number = 1000;  //从elasticsearch中搜索多少条
    	$need = $_POST["select-number"];  //需要展示多少条
    	
    	$mode = 0;
    	if($keywordany or $keywordcom){
	    	if($keywordany)
	    	{
	    		$command2 = 'python '.dirname(__FILE__).'/search.py --number='.$number.' --keywordany=\''.NewsController::unicode_encode($keywordany).'\'';
	    		// dump($command2);
	    		// dump(NewsController::unicode_encode($keywordany));
	    		$keyword = $keywordany;
	    		$title = $keywordany;
	    		$mode=1;
			}
			elseif($keywordcom)
			{
				$file_path = dirname(__FILE__)."/company-dict-multi.txt";
				if(file_exists($file_path)){
					$str = file_get_contents($file_path);
					fclose($file_path);
					$company = json_decode($str, true);
					$keywordes = $company[$keywordcom];
				}
				
	    		$command2 = 'python '.dirname(__FILE__).'/search.py --number='.$number.' --keywordcom='.$keywordes; 	
	    		// dump($command2);	
	    		$mode=2;
	    		$keyword = $keywordcom;
	    		$file_path = dirname(__FILE__)."/com-dict-reverse.txt";
				if(file_exists($file_path)){
					$str = file_get_contents($file_path);
					fclose($file_path);
					$company = json_decode($str, true);
					$title = $company[$keywordes][0];
				}
				

	    		$file_path = dirname(__FILE__)."/week_percent.txt";
				if(file_exists($file_path)){
					$str = file_get_contents($file_path);//将整个文件内容读入到一个字符串中
					fclose($file_path);
					$percent = json_decode($str, true);
					$this->assign('chart_data', json_encode($percent[$keywordes]));
				}

				$file_path = dirname(__FILE__)."/stock_value.txt";
				if(file_exists($file_path)){
					$str = file_get_contents($file_path);//将整个文件内容读入到一个字符串中
					fclose($file_path);
					$stockvalue = json_decode($str, true);
					$this->assign('chart_data2', json_encode($stockvalue[$keywordes]));
				}
			}

			
			// $command1 = escapeshellcmd('python '.dirname(__FILE__).'/search.py --keyword='.$book.' --page='.$page);
			// $output2 = shell_exec('python /usr/share/nginx/html/fin/Application/Home/Controller/search.py --number=1000 --keywordcom=600000');
			exec($command2,$output2);

			$result=json_decode($output2[0],true);

			$info=$result['hits'];
			// dump($info['hits'][3]);
			for($i = 0;$i<count($info['hits']);$i++){
				$info['hits'][$i]['_score'] = substr($info['hits'][$i]['_score'],0,4);
				$info['hits'][$i]['_source']['time'] = substr($info['hits'][$i]['_source']['time'],0,10);
				$arr = $info['hits'][$i]['_source']['stockname'];
				$str = "";
				for ($j = 0; $j < sizeof($arr); $j++) {  
			    	$str =$arr[$j].' '.$str;
				}
				$info['hits'][$i]['_source']['stockname'] = $str;
			}
			// dump($info['hits']);
			$info['hits'] = NewsController::sort_time($info['hits']);
		}
		// $this->assign('header',$output2[0]);
		if ($mode == 0 || $mode == 1){
			$this->assign('chart_data', [0]);
			$this->assign('chart_data2', [0]);
		}
		$this->assign('total',$info['total']);
		$this->assign('hits',array_slice($info['hits'], 0, $need));
		$this->assign('max_score',substr($info['max_score'], 0, 4));
		$this->assign('keyword',$keyword);
		$this->assign('title',$title);
		$this->assign('number',$need);
		$this->assign('mode',$mode);
        $this->show();
    }

	public function index2(){
		header("Content-type: text/html; charset=utf-8");
		if($_POST["sentence"]){
			$sentence = $_POST["sentence"];
			$news='';
			$object='result';
			if($sentence)
		    	{
		    		$command = 'python '.dirname(__FILE__).'/event_extraction.py --sentence=\''.NewsController::unicode_encode($sentence).'\'';
		    		// dump($command);
					exec($command, $output);		
					// dump(json_decode($output[0], true));
					$final = json_decode($output[0], true);
					$news = $final['news'];
					$object = $final['object'];
					$this->assign('object',$object);
					// $object = 600000;
					$file_path = dirname(__FILE__)."/company-dict-multi.txt";
					if(file_exists($file_path)){
						$str = file_get_contents($file_path);
						fclose($file_path);
						$company = json_decode($str, true);
						$object = $company[$object];
					}
					
					for ($i= 0; $i<sizeof($news); $i++){
						$time = $news[$i]['time'];
						$command2 = 'python '.dirname(__FILE__).'/61dayvalue.py --stock='.$object.' --date='.$time;
		    			header("Content-type: text/html; charset=utf-8");
						exec($command2, $output2);
						$ele = json_decode($output2[$i], true);
						$news[$i]['chart_data'] = json_encode($ele['value']);
						$news[$i]['date'] = json_encode($ele['date']);
					}

					$command = 'python '.dirname(__FILE__).'/preprocess.py --stock='.$object;
					// dump($command);
					exec($command);
					// dump($output3);
				}
			$this->assign('sentence',$sentence);
			$this->assign('news',$news);
			$this->assign('tag',1);
		}else{
			$this->assign('tag',0);
			$this->assign('chart_data', [0]);
			$this->assign('date', [0]);
			$this->assign('sentence','');
			$this->assign('news','');
		}
		$this->show();
	}

	public function index3(){
		header("Content-type: text/html; charset=utf-8");
		$this->show();
	}
    //排序函数
    public function sort_time($list){

    	$max = 0;
    	$res = array();
    	for($i=0;$i<sizeof($list);$i++){
    		$list[$i]['_source']['stockname'] =substr($list[$i]['_source']['stockname'],0,13);
    		$res[$i] = (int)(mktime(0,0,0,date('m'),date('d'),date('Y'))-strtotime($list[$i]['_source']['time']));
    		if ($res[$i]>$max)
    			$max = $res[$i];
    	}
    	for($i=0;$i<sizeof($list);$i++){
    		$list[$i]['time_score'] = 3*exp(-3*(float)$res[$i]/$max);
    		$list[$i]['score_score'] = (float)$list[$i]['_score']/(float)$list[0]['_score'];
    		// $list[$i]['score_score'] = 1;
    		$list[$i]['all_score'] = $list[$i]['time_score'] * $list[$i]['score_score'];
    	}

    	for($i=1;$i<sizeof($list);$i++){
    		$tmp = $list[$i];
    		$j = $i - 1;
    		while($list[$j]['all_score']<$tmp['all_score'] && $j>=0){
    			$list[$j+1] = $list[$j];
    			$j = $j - 1;
    		}
    		$list[$j+1] = $tmp;

    	}

    	return $list;
    }

    //转换编码
    public function unicode_encode($name)
	{
	    $name = iconv('UTF-8', 'UCS-2', $name);  
	    $len = strlen($name);  
	    $str = '';  
	    for ($i = 0; $i < $len - 1; $i = $i + 2)  
	    {  
	        $c = $name[$i];  
	        $c2 = $name[$i + 1];  
	        if (ord($c) > 0)  
	        {    // 两个字节的文字  
	        	if(strlen(base_convert(ord($c), 10, 16))==1){
		            $str .= '\u'.base_convert(ord($c2), 10, 16).'0'.base_convert(ord($c), 10, 16);  
		        }
		        else $str .= '\u'.base_convert(ord($c2), 10, 16).base_convert(ord($c), 10, 16);  
	        }  
	        else  
	        {  
	            $str .= $c2;  
	        }  
	    }  
	    return $str;  
	}
}