package pl.confitura.shop.architecture;

import static com.tngtech.archunit.base.DescribedPredicate.describe;
import static com.tngtech.archunit.core.domain.JavaCall.Predicates.target;
import static com.tngtech.archunit.core.domain.JavaClass.Predicates.assignableTo;
import static com.tngtech.archunit.core.domain.properties.HasName.Predicates.nameMatching;
import static com.tngtech.archunit.core.domain.properties.HasOwner.Predicates.With.owner;
import static com.tngtech.archunit.lang.syntax.ArchRuleDefinition.noClasses;
import static com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices;

import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.junit.AnalyzeClasses;
import com.tngtech.archunit.junit.ArchTest;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.library.GeneralCodingRules;
import com.tngtech.archunit.library.freeze.FreezingArchRule;
import java.math.BigDecimal;

/**
 * Bramki, których agent nie oszuka: deterministyczne, bez modelu i bez sieci,
 * kilkaset milisekund. Każda reguła mówi „dlaczego”, bo ten tekst czyta też agent.
 */
@AnalyzeClasses(packages = "pl.confitura.shop", importOptions = ImportOption.DoNotIncludeTests.class)
class ArchitectureRulesTest {

    @ArchTest
    static final ArchRule domain_does_not_depend_on_api_or_infra = noClasses()
            .that().resideInAPackage("..domain..")
            .should().dependOnClassesThat().resideInAnyPackage("..api..", "..infra..")
            .because("domena nie zna HTTP ani bazy, zob. docs/adr/0003");

    @ArchTest
    static final ArchRule services_do_not_know_each_other = slices()
            .matching("pl.confitura.shop.(*)..")
            .should().notDependOnEachOther()
            .ignoreDependency(describe("wszystko", c -> true), describe("pricing (biblioteka)", c -> c.getPackageName().startsWith("pl.confitura.shop.pricing")))
            .because("serwisy rozmawiają przez API, a wspólna jest tylko biblioteka pricing, zob. docs/adr/0003");

    @ArchTest
    static final ArchRule no_standard_streams = GeneralCodingRules.NO_CLASSES_SHOULD_ACCESS_STANDARD_STREAMS
            .because("logujemy przez logger, a nie System.out");

    @ArchTest
    static final ArchRule no_legacy_date_api = FreezingArchRule.freeze(noClasses()
            .should().dependOnClassesThat().haveFullyQualifiedName("java.util.Date")
            .orShould().dependOnClassesThat().haveFullyQualifiedName("java.text.SimpleDateFormat")
            .because("modele uczone na starym kodzie sięgają po java.util.Date; używamy java.time"));

    @ArchTest
    static final ArchRule money_arithmetic_only_in_pricing = noClasses()
            .that().resideOutsideOfPackage("..pricing..")
            .should().callMethodWhere(
                target(owner(assignableTo(BigDecimal.class)))
                .and(target(nameMatching("add|subtract|multiply|divide|setScale"))))
            .because("arytmetyka pieniędzy tylko w pricing-lib, serwisy używają Money, nie BigDecimal, zob. docs/adr/0001");
}
