import java.io.*;
import java.security.*;
import java.security.cert.X509Certificate;
import java.util.*;
import javax.xml.crypto.*;
import javax.xml.crypto.dsig.*;
import javax.xml.crypto.dsig.dom.DOMSignContext;
import javax.xml.crypto.dsig.keyinfo.*;
import javax.xml.crypto.dsig.spec.*;
import javax.xml.parsers.*;
import javax.xml.transform.*;
import javax.xml.transform.dom.DOMSource;
import javax.xml.transform.stream.StreamResult;
import org.w3c.dom.*;

public class FirmadorSRI {
    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Uso: java FirmadorSRI <xml_input> <p12_file> <p12_password> [xml_output]");
            System.exit(1);
        }

        String xmlInput = args[0];
        String p12File = args[1];
        String p12Password = args[2];
        String xmlOutput = args.length > 3 ? args[3] : null;

        DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
        dbf.setNamespaceAware(true);
        DocumentBuilder db = dbf.newDocumentBuilder();
        Document doc = db.parse(new File(xmlInput));

        // El SRI requiere que el elemento raiz tenga id="comprobante"
        Element root = doc.getDocumentElement();
        root.setIdAttribute("id", true);

        KeyStore ks = KeyStore.getInstance("PKCS12");
        ks.load(new FileInputStream(p12File), p12Password.toCharArray());

        String alias = ks.aliases().nextElement();
        PrivateKey privateKey = (PrivateKey) ks.getKey(alias, p12Password.toCharArray());
        X509Certificate cert = (X509Certificate) ks.getCertificate(alias);

        XMLSignatureFactory fac = XMLSignatureFactory.getInstance("DOM");

        List<Transform> transforms = new ArrayList<>();
        transforms.add(fac.newTransform(Transform.ENVELOPED, (TransformParameterSpec) null));
        transforms.add(fac.newTransform("http://www.w3.org/TR/2001/REC-xml-c14n-20010315", (TransformParameterSpec) null));

        // Referenciar #comprobante en lugar de documento completo
        DigestMethod digestMethod = fac.newDigestMethod(DigestMethod.SHA1, null);
        Reference ref = fac.newReference("#comprobante", digestMethod, transforms, null, null);

        CanonicalizationMethod c14n = fac.newCanonicalizationMethod(
            "http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
            (C14NMethodParameterSpec) null
        );
        SignatureMethod signMethod = fac.newSignatureMethod(SignatureMethod.RSA_SHA1, null);
        SignedInfo signedInfo = fac.newSignedInfo(c14n, signMethod, Collections.singletonList(ref));

        KeyInfoFactory kif = fac.getKeyInfoFactory();
        List<X509Certificate> x509Certs = Collections.singletonList(cert);
        X509Data x509Data = kif.newX509Data(x509Certs);
        KeyInfo keyInfo = kif.newKeyInfo(Collections.singletonList(x509Data));

        DOMSignContext dsc = new DOMSignContext(privateKey, doc.getDocumentElement());
        XMLSignature signature = fac.newXMLSignature(signedInfo, keyInfo);
        signature.sign(dsc);

        TransformerFactory tf = TransformerFactory.newInstance();
        Transformer t = tf.newTransformer();
        t.setOutputProperty(OutputKeys.OMIT_XML_DECLARATION, "no");
        t.setOutputProperty(OutputKeys.ENCODING, "UTF-8");
        t.setOutputProperty(OutputKeys.INDENT, "no");

        StringWriter sw = new StringWriter();
        t.transform(new DOMSource(doc), new StreamResult(sw));
        String xmlResult = sw.toString();
        xmlResult = xmlResult.replace("\r\n", "\n").replace("\r", "");

        if (xmlOutput != null) {
            PrintWriter pw = new PrintWriter(new OutputStreamWriter(new FileOutputStream(xmlOutput), "UTF-8"));
            pw.print(xmlResult);
            pw.close();
        } else {
            PrintWriter pw = new PrintWriter(new OutputStreamWriter(System.out, "UTF-8"));
            pw.print(xmlResult);
            pw.flush();
        }
    }
}