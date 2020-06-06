<?php
    $keywords = "";
    $emptyFlag = true;
    $urls = array();
    if($_SERVER["REQUEST_METHOD"] == "POST")
    {
        if(!empty($_POST["keywords"]))
        {
            $emptyFlag = false;
            $keywords = $_POST["keywords"];
            $pieces = explode(" ",$keywords);
            //echo count($pieces);
            //connect to database
            $myPDO = new sqlite3('SearchEngineDB.sqlite');
            $keyword = strtolower($pieces[0]);
            $q = "SELECT pid,url FROM Pages WHERE pid in(SELECT pid FROM Keywords WHERE keyword LIKE '".$keyword."%' ";
            for($i=1;$i<count($pieces);$i++)
            {
                $keyword = strtolower($pieces[$i]);
                $q .= " OR keyword LIKE '".$keyword."%' ";
            }
            $q .= ") ORDER BY newRank DESC; ";
            $result = $myPDO->query($q);
            while($row = $result->fetchArray())
            {
                //echo $row["url"];
                array_push($urls,array($row["pid"],$row["url"]));
            }
            //sort($urls);
        }
    }
?>
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* {box-sizing: border-box;}

body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
    background-color: lawngreen;
}
.search-container {
  float: right;
}

.search-container button {
  float: right;
  padding: 8px;
  margin-top: 8px;
  margin-right: 160px;
  margin-left: 10px;
  background: green;
  font-size: 17px;
  border: none;
  cursor: pointer;
    color: white;
}

.search-container button:hover {
  background: #ccc;
}
.search-container input[type=text] {
    padding:6px;
    margin-left: 150px;
  margin-top: 8px;
  font-size: 17px;
  border: none;
  border: 1px solid blue;
  width: 800px;
  }
    .heading h1{
        margin-top: 50px;
        margin-left: 250px;
        text-align: center;
        color: red;
        background-color: aliceblue;
        width: 800px;
    }
    .heading h2{
        margin-top: 100px;
        margin-left: 150px;
        color: blue;
        font-size: 30px;
    }
    .heading h3{
        margin-top: 100px;
        text-align: center;
        color: red;
        font-size: 20px;
    }
    .urls p{
        color: blue;
        margin-left: 150px;
    }
}
</style>
</head>
<body>
<div class="heading">
    <h1>ROHITH'S SEARCH ENGINE</h1>
</div>
<div class="search-container">
    <form action=<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?> method="POST">
      <input type="text" id="keywords" placeholder="Search.." name="keywords">
      <button type="submit" name="submit" value="submit">Search</button>
    </form>
</div>
<?php 
if($emptyFlag == false)
{
    if(count($urls)>0)
    { ?>
        <div class="heading">
            <h2>SEARCH RESULTS FOR<?php echo " '".$keywords."'<br>"?></h2>
        </div>
        <?php
        for($i=0;$i<count($urls);$i++)
        {?>
        <div class="urls">
            <p><a href="<?php echo $urls[$i][1]; ?>"><?php echo $urls[$i][1]; ?></a></p>
        </div>
    <?php }
        $urls = array();
    }
    else
    { ?>
        <div class="heading">
            <h3>OOPS! NO RESULTS FOUND..TRY MODIFYING WORDS IN SEARCH</h3>
        </div>
    <?php }
}
if($emptyFlag == true)
{ ?>
    <div class="heading">
        <h3>TYPE SOMETHING TO SEARCH</h3>
    </div>
<?php } ?>
</body>
</html>
