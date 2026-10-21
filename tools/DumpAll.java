import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
import java.io.*;
public class DumpAll extends GhidraScript {
  public void run() throws Exception {
    DecompInterface di=new DecompInterface(); di.openProgram(currentProgram);
    PrintWriter pw=new PrintWriter(new FileWriter(getScriptArgs()[0]));
    for (Function f: currentProgram.getFunctionManager().getFunctions(true)) {
      DecompileResults r=di.decompileFunction(f,30,monitor);
      if (r!=null && r.decompileCompleted()) pw.println("// @"+f.getEntryPoint()+"\n"+r.getDecompiledFunction().getC());
    }
    pw.close();
  }
}
