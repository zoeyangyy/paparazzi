<?php
namespace Home\Controller;
use Think\Controller;

class PaparazziController extends Controller {
	public function index(){ 
		header("Content-type: text/html; charset=utf-8");
		$this->show();
	}
	public function index2(){ 
		header("Content-type: text/html; charset=utf-8");
		$this->show();
	}
	public function star(){ 
		header("Content-type: text/html; charset=utf-8");
		$this->show();
	}
	public function movie(){ 
		header("Content-type: text/html; charset=utf-8");
		$this->show();
	}
	public function cv(){
		header("Content-type: text/html; charset=utf-8");
		if($_POST["title"]){
			$title = $_POST["title"];
 			
		   	$file_path = dirname(__FILE__)."/new_basic.json";
			if(file_exists($file_path)){
				$str = file_get_contents($file_path);
				fclose($file_path);
				$data = json_decode($str, true);
				if($data[$title]){
					$others = implode('","',$data[$title]);
				}
				else{
					echo "<script>alert('查无此人！');
					history.back();</script>"; 
				}
			} 

			$file_path = dirname(__FILE__)."/fifteen_com.json";
			if(file_exists($file_path)){
				$str = file_get_contents($file_path);
				fclose($file_path);
				$data = json_decode($str, true);
				$fifteen = implode(',',$data[$title]);
			} 

			$file_path = dirname(__FILE__)."/predict.json";
			if(file_exists($file_path)){
				$str = file_get_contents($file_path);
				fclose($file_path);
				$data = json_decode($str, true);
				$percent = $data[$title];
			}  

		}
		$this->assign('title',$title);
		$this->assign('others',$others);
		$this->assign('fifteen',$fifteen);
		$this->assign('percent',$percent);
		$this->show();
	}
}
