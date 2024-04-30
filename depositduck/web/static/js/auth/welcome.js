/**
 * (c) 2024 Alberto Morón Hernández
 */

// `/welcome/` - onboarding flow
function onboardingFormState(tenancyEndDate) {
    return {
        fields: {
            name: "",
            depositAmount: null,
            tenancyStartDate: "",
            tenancyEndDate: tenancyEndDate || "",
        },
        errors: {
            nameIsInvalid: false,
            depositAmountTooSmall: false,
            datesInWrongOrder: false,
            tenancyIsTooShort: false,
        },
        canSubmitForm: false,
        hasErrors() {
            // returns: bool
            Object.values(this.errors).some((value) => value === true);
        },
        allRequiredFieldsHaveValues() {
            // returns: bool
            const requiredFields = Object.keys(this.fields);
            return !! requiredFields.some(field => field === '' || field === null);
        },
        validateName() {
            // returns: null
            if (!this.fields.name) {
                return;
            }
            // normalise & trim spaces
            this.fields.name = this.fields.name.replace(/\s+/g, ' ').trim()
            // match Unicode letters (\p{L}), spaces (\s), apostrophe (') or dash (-)
            const pattern = /^[\p{L}\s'-]+$/u;
            this.errors.nameIsInvalid = !pattern.test(this.fields.name);
            console.log(this.fields.name, this.errors.nameIsInvalid)
        },
        validateDepositAmount() {
            // returns: null
            if (!this.fields.depositAmount) {
                return;
            }
            this.errors.depositAmountTooSmall = this.fields.depositAmount < 100;
        },
        daysBetweenDates(date1, date2) {
            // returns: number
            const diffInMs = date2 - date1;
            const msInDay = 1000 * 60 * 60 * 24;
            const diffInDays = Math.floor(diffInMs / msInDay);
            return diffInDays;
        },
        validateTenancyDates() {
            // returns: null
            if (!this.fields.tenancyStartDate) {
                return;
            }

            const gap = this.daysBetweenDates(
                new Date(this.fields.tenancyStartDate),
                new Date(this.fields.tenancyEndDate)
            );
            this.errors.datesInWrongOrder = gap < 0;
            this.errors.tenancyIsTooShort = (0 > gap && gap < 30);
        },
        validateForm() {
            // returns: null
            console.log("validateForm")
            this.validateName()
            this.validateDepositAmount();
            this.validateTenancyDates();
            this.canSubmitForm = this.allRequiredFieldsHaveValues() && !this.hasErrors();
            console.log(this.errors)
        }
    }
}
