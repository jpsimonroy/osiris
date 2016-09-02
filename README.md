Osiris
=========

Code Navigation in R
---------------------

#### :one: SHIFT + ENTER 

***Navigate to declaration.*** If multiple matches are found, the list is presented in a UI widget so that the appropriate can be selected and navigated to. The `ESC` key from the widget dismisses the widget and cancels navigation. Shift enter on a source defn i.e `source("something.r")` with attempt to navigate to the file `something.r`  

#### :two: CMD + option + F7 
***Show Usages.*** This finds usages of the selection or the word at the cursor in the entire project. If multiple matches are found, a widget is shown from which one can select the desired usage to navigate to.

#### :three: CMD + F12
***Show methods in file.*** Shows all method declarations in the currently active file. Select from the list to navigate to the declaration in file. If you are in a test file (test_that syntax), you would get to see all test methods and their contexts.

***
Snippets
---------

***mcl*** expands to mclapply 
```javascript
mclapply(range,function(x) {});
```

***test*** expands to test_that
```javascript
test_that('it should ',{
    |
});
```

***class*** expands to R5 class def
```javascript
|=setRefClass('|',
    contains=c(''),
    fields=list(),
    methods=list(
        init=function(){
            
        }
    )
);
```

***
Controlling the indexer
------------------------

You can specify ignore patterns in the plugin settings file under Preferences -> Package Settings -> Orisris -> Settings - User

```javascript
{
    "index_ignore_pattern": "_tmp_.*"
}
```

Setting the above would exclude all files with the ignore pattern from the indexer and hence its contents would not feature in any of the above shortcuts.

Like this? You may be interested in the following too.
* [Rmake](https://github.com/jpsimonroy/rmake) - Bundler for R
* [Donatello](https://github.com/jpsimonroy/donatello) - IDE support for running tests. Needs Custom project structure.
* [GoToTest](https://github.com/jpsimonroy/sublime-r-goto-test) - Toggle navigation between test and source.
* [Rmocks](https://github.com/jpsimonroy/rmocks) - R5 class mocking framework for contained unit tests in R

License
----

MIT

Authored by [Ashok Gowtham](https://github.com/ashokgowtham) and [Simon Roy](https://github.com/jpsimonroy)
