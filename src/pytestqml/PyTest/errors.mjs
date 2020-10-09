import * as Qtest from 'qtest.mjs';

class PyTestError extends Error {
  constructor(message, extra={}) {
        super(message);
        this.type = "PyTestError" // this.type because this.name gives TypeError
        this.expectFail=null
        this.expectFailMessage=""
        Object.assign(this, extra)
  }
  toString() {
    return this.type + " : " + this.message
  }

  toObj() {
    let res = {}
    for (const [k,v] of Object.entries(this)) {
        res[k] = v
    }
    res["message"] = this.message
    res["stack"] = this.stack


    return res
  }

}


class CompareError extends PyTestError {
  constructor(message, extra) {
        super(message, extra);
        this.type = "CompareError"
        this.message = this._compareFormatError() + "\n" + message;
  }
  _compareFormatError() {
           function oneParam(param) {
                if (Qtest.qtest_typeof(param) === "string")
                    param =  `"${param}"`
                else if (Qtest.qtest_typeof(param) == "object")
                    //we use qtest_typeof to avoid hang on on stringify with declarativeitem
                   param =  JSON.stringify(param)
                return param

           }
           let res =  `${oneParam(this.lhs)} != ${oneParam(this.rhs)}`
           return res
    }
}

class SkipError extends PyTestError {
  constructor(message, extra) {
        super(message, extra);
        this.type = "SkipError"
        this.message = message
  }
}
class CleanupError extends PyTestError {
  constructor(message, extra) {
        super(message, extra);
        this.type = "CleanupError"
        this.message = message
  }
}

export { CompareError, PyTestError, SkipError, CleanupError};


